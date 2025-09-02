import sys, os, glob
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 JackAnayzer <file_or_dir>")
        sys.exit(1)

    input_path = sys.argv[1]
    jack_files = []

    if os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.endswith(".jack"):
                file_path = os.path.join(input_path, file)
                jack_files.append(file_path)
    else:
        if input_path.endswith(".jack"):
            jack_files.append(input_path)

    for jack_file in jack_files:
        # output_file 생성
        output_file = jack_file.replace(".jack", ".vm")
        # 토크나이저와 엔진 생성
        tokenizer = JackTokenizer(jack_file)
        engine = CompilationEngine(tokenizer, output_file)

        engine.close()
        print("Program Complete.")

if __name__ == "__main__":
    main()
