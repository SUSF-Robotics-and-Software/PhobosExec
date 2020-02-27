from exec import PhobosExec
import argparse

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Phobos Rover Executive')
    parser.add_argument('script_path', type=str, nargs='?', default=None,
                        help='Path to the script to run, or none')

    args = parser.parse_args()

    exec = PhobosExec(args.script_path)
    exec.main_loop()