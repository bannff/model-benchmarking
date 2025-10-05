"""Tiny example showing how to import and call the package API."""
from model_benchmarking import run_benchmark

def main():
    res = run_benchmark('cs-eval')
    print('Result:', res)

if __name__ == '__main__':
    main()
