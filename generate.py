import os
import traceback
from pybliometrics.scopus import ScopusSearch, AbstractRetrieval
import json
from tqdm import tqdm

# NOTE: config file for pybliometrics is stored in $HOME/.config/pybliometrics.cfg

if __name__ == "__main__":
    # Initialize pybliometrics
    import pybliometrics
    pybliometrics.scopus.init()

    # Begin script
    for year in range(1980, 2025):
        # Make the folder to store the data for the year
        current_path = os.getcwd()
        folder_path = os.path.join(current_path, "output", str(year))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        try:
            # Get the results from ScopusSearch
            x = ScopusSearch(
                f'TITLE-ABS-KEY(AI OR "artificial intelligence" OR "hybrid intelligence" OR "collective intelligence" OR "human-machine" OR "human-AI" OR "human-bot*" OR "AI-employee*") AND ("human-agent collaboration" OR "human-agent interact*" OR "human-agent team*") AND trust* AND distrust* AND (team* OR collaborat* OR group) AND (organis* OR coordinat* OR cooperat* OR communicat* OR interact* OR manag* OR work* OR facilitat* OR innovat*) AND DOCTYPE(ar) AND PUBYEAR = {year}',
                view="STANDARD",
                cursor=False)
            print(f"Year: {year} , Results count: {len(x.results)}")

            # Store the results and add the ref_docs key to store each reference
            for doc in tqdm(x.results):
                try:
                    # Store each result in a file labeled by its Scopus EID
                    doc_dict = doc._asdict()
                    eid = doc_dict["eid"]
                    file_path = os.path.join(folder_path, f"{eid}.json")
                    if not os.path.exists(file_path):
                        # Look up the references/citations for that document
                        document = AbstractRetrieval(eid, view="REF")
                        refs = []
                        # Store the references
                        for ref in document.references:
                            ref_doc = {
                                "doi": ref.doi,
                                "title": ref.title,
                                "id": ref.id,
                                "sourcetitle": ref.sourcetitle,
                            }
                            refs.append(ref_doc)
                        doc_dict["ref_docs"] = refs
                        # Dump the dictionary to the JSON file
                        with open(file_path, "w") as json_file:
                            json.dump(doc_dict, json_file)
                    else:
                        print("SKIP (File already exists)")

                except Exception as e:
                    print(f"Error processing document {eid}: {e}")
                    traceback.print_exc()

        except Exception as e:
            print(f"Fatal error for year {year}: {e}")
            traceback.print_exc()
