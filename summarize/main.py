import re

import pandas

MACRO_TEX_PATH = r'C:\data\interactive-fl\emse\thinkmacros.tex'

macros = pandas.DataFrame(columns=[
    'aspect name',
    'aspect command',
    'short category name',
    'short category command',
    'long category name',
    'long category command',
    'legacy category name'
])

if __name__ == '__main__':
    print("loading categories...")
    with open(MACRO_TEX_PATH, 'r', encoding='utf-8') as macro_file:
        current_aspect = None
        for line in macro_file:
            line = line.strip()
            #print(line)
            aspect_match = re.search(r'.+[{](?P<command>[\\]\w+)[}][{](?P<name>[\w\s]+)[}].+%aspect$', line)
            if aspect_match:
                current_aspect = (aspect_match.group('command'), aspect_match.group('name'))
                print(f"aspect identified: {current_aspect}")
                continue
            legacy_match = re.search(r'^%LEGACY: (?P<name>[\w\s]+)', line)
            if legacy_match:
                legacy_name = legacy_match.group('name')
                line = next(macro_file)
                short_match = re.search(r'[{](?P<command>[\\]\w+)[}][{](?P<name>[\w\s]+)[}]', line)
                if short_match:
                    short_category = (short_match.group('command'), short_match.group('name'))
                    line = next(macro_file)
                    long_match = re.search(r'[{](?P<command>[\\]\w+)[}][{](?P<name>[\w\s]+)[}]', line)
                    if long_match:
                        long_category = (long_match.group('command'), long_match.group('name'))

                        print(f"{current_aspect}: {short_category}, {long_category}")
                        macros = macros.append({
                            'aspect name': current_aspect[1],
                            'aspect command': current_aspect[0],
                            'short category name': short_category[1],
                            'short category command': short_category[0],
                            'long category name': long_category[1],
                            'long category command': long_category[0],
                            'legacy category name': legacy_name
                        }, ignore_index=True)

    with open('macro_mapping.csv', 'w', encoding='utf-8') as mapping:
        mapping.write(macros.to_csv())
