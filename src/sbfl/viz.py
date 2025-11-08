from termcolor import colored

def visualize_file_with_scores(source_path: str, scores: dict, metric: str = 'tarantula'):
    '''
    Prints the source code with color highlighting based on suspiciousness scores.
    Red = high, Yellow = moderate, Green = low.
    '''
    with open(source_path, 'r') as f:
        lines = f.readlines()

    # get maximum score to normalize scale if needed
    max_score = max((scores.get(i + 1, {}).get(metric, 0) for i in range(len(lines))), default=0)

    print(f'\n===== Fault Localization ({metric}) =====\\n')
    for i, txt in enumerate(lines, start=1):
        score = scores.get(i, {}).get(metric, 0)
        if score == 0:
            color = 'white'
        elif score < 0.3:
            color = 'green'
        elif score < 0.6:
            color = 'yellow'
        else:
            color = 'red'

        print(colored(f'{i:3d}: {score:.3f} | {txt.rstrip()}', color))
