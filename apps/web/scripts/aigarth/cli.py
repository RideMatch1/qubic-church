#!/usr/bin/env python3
"""
AIGARTH CLI - LOCAL NEURAL COMPUTER

Premium command-line interface for the Aigarth system.

Usage:
    python -m aigarth.cli process "hello world"
    python -m aigarth.cli query 6+33
    python -m aigarth.cli compare "a" "b"
    python -m aigarth.cli interactive
    python -m aigarth.cli oracle "Will Bitcoin moon?"
"""

import sys
import argparse
import readline
from typing import Optional

# ANSI color codes for premium output
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Foreground
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright foreground
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Background
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'


def c(text: str, color: str) -> str:
    """Colorize text."""
    return f"{color}{text}{Colors.RESET}"


def print_banner():
    """Print the premium ASCII banner."""
    banner = f"""
{Colors.BRIGHT_CYAN}
   █████╗ ██╗ ██████╗  █████╗ ██████╗ ████████╗██╗  ██╗
  ██╔══██╗██║██╔════╝ ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║
  ███████║██║██║  ███╗███████║██████╔╝   ██║   ███████║
  ██╔══██║██║██║   ██║██╔══██║██╔══██╗   ██║   ██╔══██║
  ██║  ██║██║╚██████╔╝██║  ██║██║  ██║   ██║   ██║  ██║
  ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
{Colors.RESET}
  {Colors.DIM}LOCAL NEURAL COMPUTER v1.0{Colors.RESET}
  {Colors.DIM}Ternary Neural Network | Tick-Loop Algorithm | Anna Matrix{Colors.RESET}
"""
    print(banner)


def print_separator():
    """Print a separator line."""
    print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")


def format_energy_bar(energy: int, width: int = 40) -> str:
    """Create a visual energy bar."""
    max_energy = 64
    normalized = max(-max_energy, min(max_energy, energy))

    center = width // 2
    bar = ['░'] * width

    if normalized > 0:
        fill = int((normalized / max_energy) * center)
        for i in range(center, center + fill):
            bar[i] = '█'
    elif normalized < 0:
        fill = int((abs(normalized) / max_energy) * center)
        for i in range(center - fill, center):
            bar[i] = '█'

    bar_str = ''.join(bar)

    if energy > 0:
        return f"{Colors.BRIGHT_GREEN}{bar_str}{Colors.RESET}"
    elif energy < 0:
        return f"{Colors.BRIGHT_RED}{bar_str}{Colors.RESET}"
    else:
        return f"{Colors.YELLOW}{bar_str}{Colors.RESET}"


def format_state_pattern(states: list, width: int = 64) -> str:
    """Create a visual pattern from states."""
    pattern = []
    for i, s in enumerate(states[:width]):
        if s > 0:
            pattern.append(c('█', Colors.BRIGHT_GREEN))
        elif s < 0:
            pattern.append(c('█', Colors.BRIGHT_RED))
        else:
            pattern.append(c('░', Colors.DIM))
    return ''.join(pattern)


def cmd_process(args, engine):
    """Process an input."""
    result = engine.process(args.input, record_history=args.history)

    print()
    print(f"  {Colors.BOLD}INPUT{Colors.RESET}")
    print(f"  Raw:    {c(result.input_raw[:50], Colors.BRIGHT_WHITE)}{'...' if len(result.input_raw) > 50 else ''}")
    print(f"  Type:   {c(result.input_type.upper(), Colors.CYAN)}")
    print(f"  Length: {result.input_ternary_length} ternary bits")

    print_separator()

    print(f"  {Colors.BOLD}PROCESSING{Colors.RESET}")
    print(f"  Ticks:  {c(str(result.ticks), Colors.BRIGHT_YELLOW)}")
    print(f"  Reason: {c(result.end_reason, Colors.MAGENTA)}")
    print(f"  Time:   {result.duration_ms:.2f}ms")

    print_separator()

    print(f"  {Colors.BOLD}OUTPUT{Colors.RESET}")

    # Energy bar
    energy_color = Colors.BRIGHT_GREEN if result.energy > 0 else (Colors.BRIGHT_RED if result.energy < 0 else Colors.YELLOW)
    print(f"  Energy: {format_energy_bar(result.energy)} {c(str(result.energy), energy_color)} ({result.energy_label})")

    # Distribution
    d = result.distribution
    total = d['positive'] + d['neutral'] + d['negative']
    print(f"  Distribution:")
    print(f"    +1: {c('█' * (d['positive'] * 30 // total), Colors.GREEN)} {d['positive']}")
    print(f"     0: {c('█' * (d['neutral'] * 30 // total), Colors.YELLOW)} {d['neutral']}")
    print(f"    -1: {c('█' * (d['negative'] * 30 // total), Colors.RED)} {d['negative']}")

    # Pattern
    print(f"  Pattern:")
    print(f"    {format_state_pattern(result.state_vector)}")

    # Decoded value
    if result.decoded_value is not None:
        print(f"  Decoded: {c(str(result.decoded_value), Colors.BRIGHT_CYAN)} (0x{result.decoded_value:016X})")

    print()


def cmd_query(args, engine):
    """Query matrix position."""
    # Parse coordinates
    coord_str = args.coords.replace(',', '+')
    if '+' in coord_str:
        parts = coord_str.split('+')
        if len(parts) == 2:
            # Anna coordinates
            anna_x = int(parts[0].strip())
            anna_y = int(parts[1].strip())
            col = (anna_x + 64) % 128
            row = (63 - anna_y) % 128
        else:
            print(f"{Colors.RED}Invalid format. Use 'X+Y' or 'row,col'{Colors.RESET}")
            return
    else:
        print(f"{Colors.RED}Invalid format. Use 'X+Y' or 'row,col'{Colors.RESET}")
        return

    result = engine.query_matrix(row, col)

    print()
    print(f"  {Colors.BOLD}MATRIX QUERY{Colors.RESET}")
    print(f"  Anna Coords: {c(result['anna_format'], Colors.BRIGHT_CYAN)}")
    print(f"  Matrix Pos:  [{result['row']}, {result['col']}]")

    print_separator()

    value = result['value']
    value_color = Colors.BRIGHT_GREEN if value > 0 else (Colors.BRIGHT_RED if value < 0 else Colors.YELLOW)
    print(f"  Value:   {c(str(value), value_color)}")
    print(f"  Hex:     {result['hex']}")
    print(f"  Ternary: {c(str(result['ternary']), value_color)}")

    print_separator()

    print(f"  Neighbors:")
    print(f"    {result['neighbors'][:3]}")
    print(f"    [{result['neighbors'][3]}] {c(f'[{value}]', Colors.BOLD)} [{result['neighbors'][4]}]")
    print(f"    {result['neighbors'][5:]}")
    print(f"  Sum: {result['neighbors_sum']}")

    print()


def cmd_compare(args, engine):
    """Compare two inputs."""
    result = engine.compare(args.input_a, args.input_b)

    print()
    print(f"  {Colors.BOLD}COMPARISON{Colors.RESET}")

    print_separator()

    print(f"  Input A: {c(result['input_a'][:30], Colors.BRIGHT_CYAN)}{'...' if len(result['input_a']) > 30 else ''}")
    print(f"    Energy: {result['energy_a']}")
    print(f"    Ticks:  {result['ticks_a']}")

    print()

    print(f"  Input B: {c(result['input_b'][:30], Colors.BRIGHT_MAGENTA)}{'...' if len(result['input_b']) > 30 else ''}")
    print(f"    Energy: {result['energy_b']}")
    print(f"    Ticks:  {result['ticks_b']}")

    print_separator()

    sim = result['similarity']
    sim_color = Colors.BRIGHT_GREEN if sim > 70 else (Colors.YELLOW if sim > 40 else Colors.RED)
    print(f"  Similarity:     {c(f'{sim:.1f}%', sim_color)}")
    print(f"  Exact Matches:  {result['exact_matches']}/{128} ({result['match_percentage']:.1f}%)")
    print(f"  Energy Diff:    {result['energy_diff']}")

    print()


def cmd_oracle(args, engine):
    """Oracle mode."""
    result = engine.oracle(args.question)

    print()
    print(f"  {Colors.BOLD}ORACLE{Colors.RESET}")
    print(f"  Question: {c(result['question'], Colors.BRIGHT_WHITE)}")

    print_separator()

    answer = result['answer']
    if answer == 'YES':
        answer_str = c('YES', Colors.BRIGHT_GREEN + Colors.BOLD)
    elif answer == 'NO':
        answer_str = c('NO', Colors.BRIGHT_RED + Colors.BOLD)
    else:
        answer_str = c('UNCERTAIN', Colors.YELLOW + Colors.BOLD)

    print(f"  Answer:     {answer_str}")
    print(f"  Confidence: {result['confidence']:.0f}%")
    print(f"  Energy:     {result['energy']}")
    print(f"  Ticks:      {result['ticks']}")

    print()


def cmd_stats(args, engine):
    """Show engine statistics."""
    stats = engine.get_stats()

    print()
    print(f"  {Colors.BOLD}ENGINE STATISTICS{Colors.RESET}")

    print_separator()

    print(f"  Version:     {stats['engine_version']}")
    print(f"  Matrix:      {'LOADED' if stats['matrix_loaded'] else 'NOT LOADED'}")

    print_separator()

    print(f"  Network Configuration:")
    print(f"    Inputs:     {stats['num_inputs']}")
    print(f"    Outputs:    {stats['num_outputs']}")
    print(f"    Neighbors:  {stats['num_neighbors']}")
    print(f"    Max Ticks:  {stats['max_ticks']}")
    print(f"    Population: {stats['population']}")

    if stats['matrix_loaded']:
        print_separator()
        print(f"  Matrix Statistics:")
        print(f"    Shape:    {stats['matrix_shape']}")
        print(f"    Range:    [{stats['matrix_min']}, {stats['matrix_max']}]")
        print(f"    Mean:     {stats['matrix_mean']:.2f}")
        print(f"    Positive: {stats['positive_cells']}")
        print(f"    Negative: {stats['negative_cells']}")
        print(f"    Zero:     {stats['zero_cells']}")

    print()


def cmd_interactive(args, engine):
    """Interactive REPL mode."""
    print_banner()
    print(f"  {Colors.DIM}Type '/help' for commands, '/quit' to exit{Colors.RESET}")
    print()

    while True:
        try:
            line = input(f"{Colors.CYAN}Aigarth>{Colors.RESET} ").strip()

            if not line:
                continue

            if line.startswith('/'):
                # Command
                parts = line[1:].split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ''

                if cmd in ['quit', 'exit', 'q']:
                    print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
                    break

                elif cmd == 'help':
                    print(f"""
  {Colors.BOLD}COMMANDS{Colors.RESET}
  /help           - Show this help
  /quit           - Exit interactive mode
  /oracle <q>     - Ask yes/no question
  /compare <a> <b>- Compare two inputs
  /query <x>+<y>  - Query matrix position
  /stats          - Show engine stats
  /energy         - Show last energy
  /clear          - Clear screen

  {Colors.DIM}Just type anything to process it{Colors.RESET}
""")

                elif cmd == 'oracle' and arg:
                    result = engine.oracle(arg)
                    answer = result['answer']
                    if answer == 'YES':
                        print(f"  {c('YES', Colors.BRIGHT_GREEN)} (confidence: {result['confidence']:.0f}%)")
                    elif answer == 'NO':
                        print(f"  {c('NO', Colors.BRIGHT_RED)} (confidence: {result['confidence']:.0f}%)")
                    else:
                        print(f"  {c('UNCERTAIN', Colors.YELLOW)}")

                elif cmd == 'query' and arg:
                    # Mini query
                    try:
                        parts = arg.replace(',', '+').split('+')
                        anna_x = int(parts[0].strip())
                        anna_y = int(parts[1].strip())
                        col = (anna_x + 64) % 128
                        row = (63 - anna_y) % 128
                        result = engine.query_matrix(row, col)
                        value = result['value']
                        value_color = Colors.GREEN if value > 0 else (Colors.RED if value < 0 else Colors.YELLOW)
                        print(f"  [{anna_x}+{anna_y}] = {c(str(value), value_color)}")
                    except:
                        print(f"  {Colors.RED}Invalid format{Colors.RESET}")

                elif cmd == 'stats':
                    stats = engine.get_stats()
                    print(f"  Matrix: {'LOADED' if stats['matrix_loaded'] else 'NOT LOADED'}")
                    print(f"  Network: {stats['num_inputs']}→{stats['num_outputs']} neurons")

                elif cmd == 'clear':
                    print('\033[2J\033[H')
                    print_banner()

                else:
                    print(f"  {Colors.RED}Unknown command: /{cmd}{Colors.RESET}")

            else:
                # Process input
                result = engine.process(line)

                energy_color = Colors.GREEN if result.energy > 0 else (Colors.RED if result.energy < 0 else Colors.YELLOW)
                print(f"  Energy: {c(str(result.energy), energy_color)} | Ticks: {result.ticks} | {result.end_reason}")
                print(f"  Pattern: {format_state_pattern(result.state_vector, 32)}")

        except KeyboardInterrupt:
            print(f"\n{Colors.DIM}Use /quit to exit{Colors.RESET}")
        except EOFError:
            print(f"\n{Colors.DIM}Goodbye!{Colors.RESET}\n")
            break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AIGARTH - Local Neural Computer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process "Hello World"
  %(prog)s query 6+33
  %(prog)s compare "Bitcoin" "bitcoin"
  %(prog)s oracle "Will it work?"
  %(prog)s interactive
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Process command
    p_process = subparsers.add_parser('process', help='Process an input through the network')
    p_process.add_argument('input', help='Input to process')
    p_process.add_argument('--history', action='store_true', help='Record tick history')

    # Query command
    p_query = subparsers.add_parser('query', help='Query a matrix position')
    p_query.add_argument('coords', help='Coordinates (e.g., 6+33 or 30,70)')

    # Compare command
    p_compare = subparsers.add_parser('compare', help='Compare two inputs')
    p_compare.add_argument('input_a', help='First input')
    p_compare.add_argument('input_b', help='Second input')

    # Oracle command
    p_oracle = subparsers.add_parser('oracle', help='Yes/No oracle')
    p_oracle.add_argument('question', help='Question to ask')

    # Stats command
    p_stats = subparsers.add_parser('stats', help='Show engine statistics')

    # Interactive command
    p_interactive = subparsers.add_parser('interactive', help='Interactive REPL mode')

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return

    # Initialize engine
    from .core.engine import AigarthEngine
    engine = AigarthEngine()

    if not engine.matrix_loaded:
        print(f"{Colors.YELLOW}Warning: Matrix not loaded. Some features may not work.{Colors.RESET}")

    # Run command
    if args.command == 'process':
        cmd_process(args, engine)
    elif args.command == 'query':
        cmd_query(args, engine)
    elif args.command == 'compare':
        cmd_compare(args, engine)
    elif args.command == 'oracle':
        cmd_oracle(args, engine)
    elif args.command == 'stats':
        cmd_stats(args, engine)
    elif args.command == 'interactive':
        cmd_interactive(args, engine)


if __name__ == '__main__':
    main()
