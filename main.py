# main.py
from scraper import extract_text_from_url
from summarizer import ask_llm

def main():
    print("🤖 Ask me anything! I’ll search and answer using live websites.")
    query = input("Your question: ")

    urls = []
    print("Enter up to 3 URLs (press enter to stop):")
    for _ in range(3):
        url = input("URL: ").strip()
        if not url:
            break
        urls.append(url)

    print("\n🔍 Scraping and analyzing...")
    docs = [extract_text_from_url(url) for url in urls]
    docs = [d for d in docs if d]  # remove failed scrapes

    if not docs:
        print("❌ No content retrieved. Try different URLs.")
        return

    answer = ask_llm(query, docs)
    print("\n🧠 Answer:\n")
    print(answer)

if __name__ == "__main__":
    main()
