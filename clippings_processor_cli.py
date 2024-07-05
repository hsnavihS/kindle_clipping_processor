import sys
from HighlightProcessor import HighlightProcessor

def main():
    num_args = len(sys.argv)
    if num_args != 3 or sys.argv[1] not in ["-t", "-p"]:
        print(("Usage: python clippings_processor_cli.py <mode> <filename.txt>\n"
            "eg: python clippings_processor_cli.py -t \"My Clippings.txt\" :: for running in test mode\n"
            "eg: python clippings_processor_cli.py -p \"My Clippings.txt\" :: for running in production mode"))
        sys.exit(1)

    filename = sys.argv[2]

    mode = "test"
    if sys.argv[1] == "-p":
        mode = "prod"
    processor = HighlightProcessor(filename, mode)
    processor.process_file()
    exit(0)

if __name__ == "__main__":
    main()
