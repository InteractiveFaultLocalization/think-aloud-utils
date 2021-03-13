import re
from math import isnan
import matplotlib.pyplot as plt
import seaborn as sns

import pandas
from matplotlib.figure import Figure

import networkx as nx

MACRO_TEX_PATH = r'C:\data\interactive-fl\emse\thinkmacros.tex'
NOTE_PATH = r'C:\data\think-aloud-toolkit\summarize\think-aloud videók kategórizálás és szempontok.txt'


def load_category_macros() -> pandas.DataFrame:
    macros = pandas.DataFrame(columns=[
        'aspect name',
        'aspect command',
        'short category name',
        'short category command',
        'long category name',
        'long category command',
        'legacy category name'
    ])
    with open(MACRO_TEX_PATH, 'r', encoding='utf-8') as macro_file:
        current_aspect = None
        for line in macro_file:
            line = line.strip()
            aspect_match = re.search(r'.+[{](?P<command>[\\]\w+)[}][{](?P<name>[^}]+)[}].+%aspect$', line)
            if aspect_match:
                current_aspect = (aspect_match.group('command'), aspect_match.group('name'))
                continue
            legacy_match = re.search(r'^%LEGACY: (?P<name>.+)$', line)
            if legacy_match:
                legacy_name = legacy_match.group('name').strip()
                line = next(macro_file)
                short_match = re.search(r'[{](?P<command>[\\]\w+)[}][{](?P<name>[^}]+)[}]', line)
                if short_match:
                    short_category = (short_match.group('command'), short_match.group('name'))
                    line = next(macro_file)
                    long_match = re.search(r'[{](?P<command>[\\]\w+)[}][{](?P<name>[^}]+)[}]', line)
                    if long_match:
                        long_category = (long_match.group('command'), long_match.group('name'))
                        macros = macros.append({
                            'aspect name': current_aspect[1],
                            'aspect command': current_aspect[0],
                            'short category name': short_category[1],
                            'short category command': short_category[0],
                            'long category name': long_category[1],
                            'long category command': long_category[0],
                            'legacy category name': legacy_name
                        }, ignore_index=True)
    return macros


def load_categorization() -> pandas.DataFrame:
    categorization = pandas.DataFrame(columns=['legacy category name', 'vsz id', 'category rank', 'section name'])
    with open(NOTE_PATH, 'r', encoding='utf-8') as note_file:
        current_vsz = None
        for line in note_file:
            line = line.strip()
            vsz_match = re.search(r'^vsz\.\s+(?P<id>[1-6])', line)
            if vsz_match:
                current_vsz = vsz_match.group('id')
                continue
            section_match = re.search(r'^[(](?P<name>[\w-]+)[)]\s+(?P<list>.+)$', line)
            if section_match:
                section_name = section_match.group('name')
                categories = [legacy_name.strip() for legacy_name in section_match.group('list').strip(';').split(';')]
                for index, legacy_name in enumerate(categories):
                    if legacy_name not in ['none']:
                        categorization = categorization.append({
                            'legacy category name': legacy_name,
                            'vsz id': current_vsz,
                            'category rank': index,
                            'section name': section_name
                        }, ignore_index=True)
    return categorization


def generate_category_by_rareness_figure():
    y = categorization['aspect name'] + ' / ' + categorization['short category name']
    x = categorization['section name']
    z = categorization['category rank'] + 1
    fig: Figure
    ax: plt.Axes
    fig, ax = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(15)
    sns.swarmplot(
        x=x, y=y, hue=z,
        dodge=True,
        palette=sns.dark_palette('white'),
        edgecolor='black',
        linewidth=1,
        size=5,
        ax=ax)
    ax.get_legend().set_title('Rareness of manifestation')
    ax.set_ylabel('Categories')
    ax.set_xlabel('Sections')
    ax.set_xticklabels(['Routine workflow', 'After feature demonstration', 'After use-case discussion'])
    fig.tight_layout()
    # fig.show()
    fig.savefig('category_by_rareness.pdf', bbox_inches='tight')


def node_id(category_record, section):
    return f'{category_record["short category name"]} ({section})'
    # return f'{category_record["short category name"]}'


def _connect_to_from(from_categorization, to_categorization, from_section, to_section):
    for from_index, from_category in from_categorization.iterrows():
        for to_index, to_category in to_categorization.iterrows():
            if from_category['vsz id'] == to_category['vsz id']:
                from_node = node_id(from_category, from_section)
                to_node = node_id(to_category, to_section)
                from_rank = from_category['category rank']
                to_rank = to_category['category rank']
                if from_rank < to_rank:
                    change = 'greater'
                elif to_rank < from_rank:
                    change = 'less'
                else:
                    change = 'equal'
                graph.add_edge(
                    from_node, to_node,
                    developer=from_category['vsz id'], cause=to_section,
                    from_rank=from_rank, to_rank=to_rank, change=change,
                    const='const'
                )


def _create_nodes(section, _macros):
    for index, category in _macros.iterrows():
        graph.add_node(
            node_id(category, section),
            label=f'{category["aspect name"]} / {category["short category name"]}\n({section})',
            category=category['short category name'], aspect=category['aspect name'], const='const')


if __name__ == '__main__':
    print("loading categories...", end='')
    macros = load_category_macros()
    with open('macro_mapping.csv', 'w', encoding='utf-8') as mapping:
        mapping.write(macros.to_csv())
    print("done")

    print("loading categorization...", end='')
    categorization = load_categorization()
    categorization = categorization.join(macros.set_index('legacy category name'), on='legacy category name')
    for record in categorization.values:
        for value in record:
            if isinstance(value, float) and isnan(value):
                raise ValueError("missing or corrupted data")
    print("done")

    print("generating category by rareness...", end='')
    generate_category_by_rareness_figure()
    print("done")

    for aspect in macros['aspect name'].unique():
        print(f"generating category arches for {aspect}...", end='')
        category_is_aspect = categorization['aspect name'] == aspect
        macros_is_aspect = macros['aspect name'] == aspect
        aspect_macros = macros[macros_is_aspect]

        graph = nx.DiGraph()

        graph.add_node(
            'from_legend',
            label=f'Aspect / Category\n(Section)'
        )
        graph.add_node(
            'less_legend',
            label=f'Aspect / Category\n(Section)'
        )
        graph.add_node(
            'equal_legend',
            label=f'Aspect / Category\n(Section)'
        )
        graph.add_node(
            'greater_legend',
            label=f'Aspect / Category\n(Section)'
        )
        graph.add_edge(
            'from_legend', 'less_node',
            legend=f'color = subject'
        )

        _create_nodes('routine', aspect_macros)
        _create_nodes('feature', aspect_macros)
        _create_nodes('use-case', aspect_macros)

        is_routine_and_aspect = (categorization['section name'] == 'routine') & category_is_aspect
        is_feature_and_aspect = (categorization['section name'] == 'feature') & category_is_aspect
        is_use_case_and_aspect = (categorization['section name'] == 'use-case') & category_is_aspect
        _connect_to_from(
            categorization[is_routine_and_aspect], categorization[is_feature_and_aspect],
            'routine', 'feature')
        _connect_to_from(
            categorization[is_feature_and_aspect], categorization[is_use_case_and_aspect],
            'feature', 'use-case')

        graph.remove_nodes_from(list(nx.isolates(graph)))

        nx.write_graphml(graph, f'arcs_in_{aspect}.graphml')
        print("done")

    print()