import re
from .constants import ASS_HEADER, NO_MERGE, AUTO_MERGE, FORCE_MERGE
from .config import Config
from .tap_dialogue import TapDialogue


class TapAssParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.actor_record = {}

    def __iter__(self):
        return self.iterate_events()

    def iterate_events(self):
        for index, event in enumerate(self.events):
            yield index, event

    def parse(self) -> 'TapAssParser':
        self.events = []
        self.y_spacing = 0
        with open(self.file_path, 'r', encoding='utf-8_sig') as ass_file:
            for line in ass_file:
                if line.startswith('Dialogue:') and ',Rubi,' not in line:
                    event = TapDialogue(
                        line).convert_full_half_width_characters()
                    self.events.append(event)
                elif 'ResY:' in line:
                    res_y = int(re.search(r'ResY: ?(\d+)', line).group(1))
                    self.y_spacing = int(60*(res_y/540))

        return self

    def process(self, user_config: Config) -> 'TapAssParser':
        self.set_actor()
        self.merge_duplicate_rows_by_time(user_config.merge)
        del_list = []

        for index, line in self:
            line.text = line.clean_up_text().text_stripped
            if user_config.clean_mode:
                line.clean_trash()
            if line.text == '':
                del_list.append(index)
                continue

            if user_config.add_spaces:
                line.add_space()
            if user_config.adjust_repeated_syllables:
                line.adjust_repeated_syllables()

        self.remove_lines(del_list)
        return self

    def set_actor(self) -> 'TapAssParser':
        none_actor_index = 1
        same_actor_flag = False

        for index, line in self:
            # Three types of actor: parentheses, colon, color
            actor = None
            text_stripped = re.sub(r'{[^}]+}', '', line.text_stripped)

            # Find the specific speaker
            if text_stripped.startswith('(') and ')' in text_stripped:
                actor = re.search(r'\((.*?)\)', text_stripped).group(1)
                same_actor_flag = False
            elif '：' in text_stripped and text_stripped.index('：') < 8:
                actor = text_stripped[:text_stripped.index('：')]
                same_actor_flag = False

            if '\\c&' in line.text:  # Set the speaker based on the color
                text = re.sub(
                    r'{\\c&[0-9a-fhA-FH][^}]*}[　 ]*{\\c&H00FFFFFF[^}]*}', '', line.text)
                if '\\c&' in text:
                    color_index = line.text.find('\\c&')
                    color = line.text[color_index+4:color_index+4+8]
                    if color not in self.actor_record:
                        self.actor_record[color] = actor or str(
                            none_actor_index)
                    elif not actor:
                        actor = self.actor_record[color]
            else:  # Set the speaker based on parentheses or coordinates
                if same_actor_flag or index > 0 and self.events[index-1].text.endswith(('→', '➡')):
                    actor = self.events[index-1].actor
                if text_stripped.startswith(('<', '＜', '《', '｟', '≪')):
                    same_actor_flag = True
                if text_stripped.endswith(('>', '＞', '》', '｠', '≫')):
                    same_actor_flag = False
                if not actor and not same_actor_flag and index > 0:
                    last_line = self.events[index-1]
                    if (line.start, line.end) == (last_line.start, last_line.end) and not '\\c&' in last_line.text and (line.pos_y and last_line.pos_y) and abs(line.pos_y-last_line.pos_y) <= self.y_spacing:
                        actor = last_line.actor
            if actor:
                line.actor = actor
            else:
                line.actor = str(none_actor_index)
                none_actor_index += 1

        return self

    def remove_lines(self, indexes_to_remove) -> 'TapAssParser':
        for index in sorted(indexes_to_remove, reverse=True):
            self.events.pop(index)
        return self

    def merge_duplicate_rows_by_time(self, mode=AUTO_MERGE) -> 'TapAssParser':
        if mode not in [AUTO_MERGE, NO_MERGE, FORCE_MERGE]:
            raise ValueError(f"Invalid mode.")

        if mode == NO_MERGE:
            return self

        del_list = []

        for index in range(len(self.events)-1):
            event = self.events[index]
            next_event = self.events[index+1]
            if event.start == next_event .start and event.end == next_event.end:
                if event.actor == next_event.actor:
                    next_event.text = event.text + '\u3000' + next_event.text
                    if mode == AUTO_MERGE:
                        next_event.text = next_event.text.replace(
                            '？\u3000', '？').replace('！\u3000', '！')
                    del_list.append(index)
                elif mode == FORCE_MERGE:
                    next_event.actor = event.actor + '/' + next_event.actor
                    next_event.text = event.text + '\n' + next_event.text
                    del_list.append(index)

        self.remove_lines(del_list)

        return self

    def write_txt(self, output_path: str, output_actor: bool = False, ending_char: str = ''):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for line in self.events:
                text = line.replace('\n', '\u3000')
                output_file.write(
                    f'[{line.actor}]\t{text}\n' if output_actor else f'{text}{ending_char}\n')

    def write_ass(self, output_path: str, output_actor: bool = False, ending_char: str = ''):
        with open(output_path, 'w', encoding='utf-8_sig') as output_file:
            output_file.write(ASS_HEADER)
            for line in self.events:
                text = line.replace('\n', '\\N')
                output_file.write(
                    f'Dialogue: 0,{line.start},{line.end},JP,{line.actor or "" if output_actor else ""},0,0,0,,{text}{ending_char}\n')

    def write_srt(self, output_path: str, output_actor: bool = False, ending_char: str = ''):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for i, line in self:
                output_file.write(
                    '%d\n%s --> %s\n%s%s%s\n\n' % (i+1, f'0{line.start.replace(".", ",")}', f'0{line.end.replace(".",",")}',
                                                   f'{{{line.actor}}}' if output_actor and line.actor else '', line.text, ending_char))
