import argparse
import os
import re
from math import isnan
import matplotlib.pyplot as plt
import numpy
import seaborn as sns

import pandas
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure

import networkx as nx

MACRO_TEX_PATH = r'C:\data\interactive-fl\emse\thinkmacros.tex'
NOTE_PATH = r'C:\data\interactive-fl\emse\think-aloud videók kategórizálás és szempontok.txt'


def load_category_macros_from_tex() -> pandas.DataFrame:
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


def load_categorization_from_raw_notes() -> pandas.DataFrame:
    categorization = pandas.DataFrame(columns=['legacy category name', 'participant', 'category rank', 'phase name'])
    with open(NOTE_PATH, 'r', encoding='utf-8') as note_file:
        current_vsz = None
        for line in note_file:
            line = line.strip()
            vsz_match = re.search(r'^vsz\.\s+(?P<id>[1-6])', line)
            if vsz_match:
                current_vsz = vsz_match.group('id')
                continue
            phase_match = re.search(r'^[(](?P<name>[\w-]+)[)]\s+(?P<list>.+)$', line)
            if phase_match:
                phase_name = phase_match.group('name')
                categories = [legacy_name.strip() for legacy_name in phase_match.group('list').strip(';').split(';')]
                for index, legacy_name in enumerate(categories):
                    if legacy_name not in ['none']:
                        categorization = categorization.append({
                            'legacy category name': legacy_name,
                            'participant': current_vsz,
                            'category rank': index,
                            'phase name': phase_name
                        }, ignore_index=True)
    return categorization


def generate_category_by_rareness_heatmap(_categorization, phase, y_label=True):
    interesting_columns = ['unique name', 'participant', 'category rank']
    heat_mapped = _categorization[interesting_columns].groupby(by=['unique name', 'participant']).sum().unstack('participant')
    present = set(heat_mapped.index)
    all_category = set(categorization['unique name'].unique())
    missings = all_category - present
    for missing in missings:
        heat_mapped.loc[missing] = numpy.nan
    heat_mapped.sort_index(inplace=True)

    fig: Figure
    ax: plt.Axes
    fig, ax = plt.subplots()
    fig.set_figheight(10)
    fig.set_figwidth(10)
    heatmap = ax.imshow(heat_mapped, cmap=LinearSegmentedColormap.from_list('gery', ['black', 'gainsboro']))
    for x, column in enumerate(heat_mapped.columns):
        for y, index in enumerate(heat_mapped.index):
            entry = heat_mapped[column][index]
            if not isnan(entry):
                text = ax.text(x, y, str(6 - int(entry)), ha="center", va="center", color="w")

    ax.set_xlabel('Participants')
    indexes = heat_mapped.index
    ax.set_yticks(numpy.arange(len(indexes)))
    if y_label:
        ax.set_ylabel('Categories')
        ax.set_yticklabels(indexes)
    else:
        ax.set_ylabel('')
        ax.set_yticklabels([''] * len(indexes))
    ax.set_xticks(numpy.arange(6))
    ax.set_xticklabels(range(1, 7))
    fig.tight_layout()
    # fig.show()
    fig.savefig(f'category_by_rareness_{phase}_{"label" if y_label else "no-label"}_heatmap.pdf', bbox_inches='tight')


def generate_category_by_rareness_figure(_categorization):
    _categorization['unique name'] = _categorization['aspect name'] + ' / ' + _categorization['short category name']

    y = _categorization['unique name']
    x = _categorization['phase name']
    z = _categorization['category rank'].map(
        {
            0: 'mostly observed',
            1: 'very common',
            2: 'common',
            3: 'rare',
            4: 'very rare',
            5: 'almost absent'
        })
    fig: Figure
    ax: plt.Axes
    fig, ax = plt.subplots()
    fig.set_figheight(8)
    fig.set_figwidth(15)
    sns.swarmplot(
        x=x, y=y, hue=z,
        palette=sns.dark_palette('white'),
        edgecolor='black',
        linewidth=1,
        size=10,
        marker='s',
        ax=ax)
    ax.set_ylabel('Categories')
    ax.set_xlabel('Sections')
    ax.set_xticklabels(['Routine workflow', 'After feature demonstration', 'After use-case discussion'])
    fig.tight_layout()
    # fig.show()
    fig.savefig('category_by_rareness.pdf', bbox_inches='tight')


def node_id(category_record, phase):
    return f'{category_record["aspect name"]}/{category_record["short category name"]} ({phase})'


edge_id = 0


def _connect_to_from(from_categorization, to_categorization,
                     from_phase, to_phase,
                     graph):
    global edge_id
    for from_index, from_category in from_categorization.iterrows():
        for to_index, to_category in to_categorization.iterrows():
            from_vsz_id = from_category['participant']
            to_vsz_id = to_category['participant']
            is_vsz_id_same = from_vsz_id == to_vsz_id
            is_aspect_same = from_category['aspect name'] == to_category['aspect name']
            if is_vsz_id_same and is_aspect_same:
                from_node = node_id(from_category, from_phase)
                to_node = node_id(to_category, to_phase)
                join_node = from_node + to_node
                graph.add_node(
                    join_node,
                    label=f'from: {from_category["short category name"]}\nto: {to_category["short category name"]}',
                    **{'from_' + key: _value for key, _value in from_category.items() if 'command' not in key},
                    **{'to_' + key: _value for key, _value in from_category.items() if 'command' not in key},
                    style='join'
                )
                graph.add_edge(
                    from_node, join_node, key=edge_id,
                    **{'from_' + key: _value for key, _value in from_category.items() if 'command' not in key},
                    style='from'
                )
                edge_id += 1
                graph.add_edge(
                    join_node, to_node, key=edge_id,
                    **{'to_' + key: _value for key, _value in from_category.items() if 'command' not in key},
                    style='to'
                )
                edge_id += 1


def _create_nodes(phase, _macros, graph):
    for index, category in _macros.iterrows():
        graph.add_node(
            node_id(category, phase),
            label=f'{category["short category name"]}\n({phase})',
            **{key: _value for key, _value in category.items() if 'command' not in key},
            style='category')


def generate_arch_graph(filter_name, category_filter, macros_filter):
    filtered_macros = macros[macros_filter]
    graph = nx.MultiDiGraph()
    _create_nodes('routine', filtered_macros, graph)
    _create_nodes('feature', filtered_macros, graph)
    _create_nodes('use-case', filtered_macros, graph)
    is_routine = (categorization['phase name'] == 'routine') & category_filter
    is_feature = (categorization['phase name'] == 'feature') & category_filter
    is_use_case = (categorization['phase name'] == 'use-case') & category_filter
    _connect_to_from(
        categorization[is_routine], categorization[is_feature],
        'routine', 'feature', graph)
    _connect_to_from(
        categorization[is_feature], categorization[is_use_case],
        'feature', 'use-case', graph)
    graph.remove_nodes_from(list(nx.isolates(graph)))
    nx.write_graphml(
        graph,
        f'arcs_{filter_name}.graphml')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--macros', type=str, default=None, help='CSV file containing the aspects and categories')
    parser.add_argument(
        '--categorization', type=str, default=None,
        help='CSV file containing the categorization of the behavior of the participants')
    args = parser.parse_args()

    if os.path.isfile(args.macros) and os.path.isfile(args.categorization):
        print("loading preprocessed data...", end='')
        macros = pandas.read_csv(args.macros)
        categorization = pandas.read_csv(args.categorization)
        print("done")
    else:
        print("loading raw data")
        print("loading categories...", end='')
        macros = load_category_macros_from_tex()
        with open('macros.csv', 'w', encoding='utf-8') as macros_file:
            macros_file.write(macros.to_csv())
        print("done")

        print("loading categorization...", end='')
        categorization = load_categorization_from_raw_notes()
        categorization = categorization.join(macros.set_index('legacy category name'), on='legacy category name')
        categorization['unique name'] = categorization['aspect name'] + ' / ' + categorization['short category name']

        with open('categorization.csv', 'w', encoding='utf-8') as categorization_file:
            categorization_file.write(categorization.to_csv())
        print("done")

        for record in categorization.values:
            for value in record:
                if isinstance(value, float) and isnan(value):
                    raise ValueError("missing or corrupted data")
        print("done")

    print("generating category by rareness...", end='')
    generate_category_by_rareness_figure(categorization.copy())
    print("done")

    print("generating category by rareness heatmap...", end='')
    for phase in categorization['phase name'].unique():
        is_phase = categorization['phase name'] == phase
        generate_category_by_rareness_heatmap(categorization[is_phase].copy(), phase)
        generate_category_by_rareness_heatmap(categorization[is_phase].copy(), phase, y_label=False)
    print("done")

    for aspect in macros['aspect name'].unique():
        print(f"generating category arches for {aspect}...", end='')
        generate_arch_graph(aspect, category_filter=categorization['aspect name'] == aspect,
                            macros_filter=macros['aspect name'] == aspect)
        print("done")
    print(f"generating category arches for full...", end='')
    generate_arch_graph('full', category_filter=[True] * len(categorization.index),
                        macros_filter=[True] * len(macros.index))
    print("done")

    raw_counts = categorization.groupby(by=['aspect command', 'short category command', 'phase name']).count()
    counts = {}
    for by, entry in raw_counts.iterrows():
        aspect, category, phase = by
        count = entry['participant']
        if aspect not in counts:
            counts[aspect] = {}
        if category not in counts[aspect]:
            counts[aspect][category] = {'routine': '', 'feature': '', 'use-case': ''}
        counts[aspect][category][phase] = count if count > 0 else ''
        assert 0 <= count <= 6

    with open('table.tex', 'w', encoding='utf-8') as table_file:
        for aspect, categories_count in counts.items():
            table_file.write(r'\begin{table}\centering' + '\n')
            table_file.write(r'\begin{tabular}{@{}lccc@{}}' + '\n')
            table_file.write(r'\toprule' + '\n')
            table_file.write(r'&\header{routine}&\header{feature}&\header{use-case}\\')
            table_file.write(r'\midrule' + '\n')
            for category, phases_count in categories_count.items():
                table_file.write(
                    f'\\header{{{category}}}&'
                    f'{phases_count["routine"]}&{phases_count["feature"]}&{phases_count["use-case"]}\\\\\n')
            table_file.write(r'\bottomrule' + '\n')
            table_file.write(r'\end{tabular}' + '\n')
            table_file.write(
                f'\\caption{{Count of categories'
                f' during various phases'
                f' regarding \\enquote{{{aspect}}} aspect}}' + '\n')
            table_file.write(r'\end{table}' + '\n')
