import parser.database_manipulation as parser


def download_and_process_key(key):
    print(key)
    result = []
    result.append(parser.start(key))
    print(result)
    del result[0]