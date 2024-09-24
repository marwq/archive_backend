from src.application.vectordb import Doc, initialize_pinecone, search_text, text_to_vector


def main():
    index = initialize_pinecone()

    random_doc = Doc(id="1", text="In 1492, Columbus sailed the ocean blue.")
    vector = text_to_vector(random_doc, index)

    random_doc = Doc(id="2", text="Hello, World!")
    vector = text_to_vector(random_doc, index)

    random_doc = Doc(id="3", text="Goldfish are a common household pet.")
    vector = text_to_vector(random_doc, index)

    print(f"Document added to Pinecone. Vector: {vector[:5]}...")

    search_results = search_text("Goldfish", index)
    print(search_results)


if __name__ == "__main__":
    main()
