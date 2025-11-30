import argparse
import json
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("path", help="path to raw_export.txt")
    parser.add_argument("-o", "--output", help="output directory")
    parser.add_argument("-j", "--json", action='store_true', help="export as json (to stdout)")
    args = parser.parse_args()

    global articles
    articles = []

    with open(args.path, encoding='utf-8') as f:
        lines = f.readlines()
        lines = [line.rstrip("\n") for line in lines]
        # print(lines[0:10])

        global article, bodies, is_header
        article = {}
        bodies = []
        is_header = True

        def finalize_article():
            global articles, article, bodies, is_header
            is_header = True
            article["body"] = '\n'.join(bodies)
            articles.append(article)
            article = {}

        for line in lines:
            if line == "-----":
                if is_header:
                    is_header = False
                    bodies = []
                else:
                    finalize_article()
            elif line == "--------":
                pass
                # just ignore
            elif line.startswith("BODY:"):
                is_header = False
                # and ignore
            elif is_header:
                lst = line.split(': ')
                key = lst[0].lower()
                value = ""
                if len(lst) > 1:
                    value = lst[1]

                article[key] = value
            elif not is_header:
                bodies.append(line)
            else:
                raise "unreachable"
            
        if "title" in article and "body" in article:
            finalize_article()

    if args.json:
        obj = {"count": len(articles), "articles": articles}
        s = json.dumps(obj, ensure_ascii=False)
        print(s)
        sys.exit()

    print(f"count: {len(articles)}")

    print(articles[0])

    for article in articles:
        if "title" in article and "body" in article:
            title = article["title"]
            print(f"title: {title}")
