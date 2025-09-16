import argparse
from app.services.sentiment_service import analyze_text, analyze_csv
import asyncio
from app.services.sentiment_service import analyze_mongo

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["test", "analyze", "mongodb"], required=True)
    parser.add_argument("--text", type=str, help="텍스트 입력")
    parser.add_argument("--csv", type=str, help="CSV 파일 경로")
    parser.add_argument("--limit", type=int, default=1000, help="Mongo 분석 개수")
    args = parser.parse_args()

    if args.mode == "test" and args.text:
        print(analyze_text(args.text))

    elif args.mode == "analyze" and args.csv:
        print(analyze_csv(args.csv))

    elif args.mode == "mongodb":
        asyncio.run(analyze_mongo(limit=args.limit))
