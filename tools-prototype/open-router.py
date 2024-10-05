import os
import sys
import csv
import time
import re
import requests
import json

# Add your OpenRouter API key here
OPENROUTER_API_KEY = "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"
model="nousresearch/hermes-3-llama-3.1-405b"

def generate_title(clean, ptitle):
    try:
        messages = [
            {"role": "system", "content": f"<|im_start|>system\nYou are Hermes, an assistant who demonstrates expertise in meticulously documenting and analyzing academic texts.<|im_end|>"},
            {"role": "user", "content": f"<|im_start|>user\n```This new understanding of the multifaceted roles of the cranial nerves, and particularly their connection with the state of social engagement, enabled me to consistently help more people with an even wider range of health issues. All I had to do was to determine whether these five cranial nerves functioned well and, if not, to use a technique to get them to function better. This made it possible for me to achieve far greater success in my practice and to treat intransigent conditions such as migraine headaches, depression, fibromyalgia, COPD, post-traumatic stress, forward head posture, and neck and shoulder problems, among others. This book is an introduction to the theory and practice of Polyvagal healing. After describing basic neurological structures, I will list some of the physical, psychological, and social issues caused by dysfunctions of those five cranial nerves. According to the Polyvagal Theory, the autonomic nervous system has two other functions in addition to those of the ventral branch of the vagus nerve: the activity of the dorsal branch of the vagus nerve, and sympathetic activity from the spinal chain. This multiple (poly-) nature of the vagus nerve gives the theory its name. The differences between the functions of the ventral and dorsal branches of the vagus nerve have profound implications for physical and behavioral health and healing. Throughout the book, I propose a new approach to healing that includes self-help exercises and hands-on therapeutic techniques that are simple to learn and easy to use. It is my hope that this knowledge will continue to spread and enable many more people to help themselves and others. RESTORING SOCIAL ENGAGEMENT I have written this book to make the benefits of restoring vagal function available to a broad range of people, even if they have no prior experience with craniosacral or other forms of hands-on therapy. Readers can acquire a unique set of easy-to-learn and easy-to-do self-help exercises and hands-on techniques that should enable them to improve the function of these five nerves in themselves and others. I used the principles behind Alain Gehin's work to develop these techniques. The exercises and techniques restore flexibility to the functioning of the autonomic nervous system. They can help eliminate the general adverse conditions of chronic stress, which arises from the overstimulation of the spinal sympathetic chain, and depressive behavior and shut-down, which arise from activity in the dorsal vagal circuit. The exercises are noninvasive and do not involve medicine or surgery.```\n\nThe content between backticks is a subsection of a book-chapter. Write fewer than 20 words to concisely describe this passage, without prefix or any further explanation.<|im_end|>"},
            {"role": "assistant", "content": f"<|im_start|>assistant\nRestoring Autonomic Balance Through Cranial Nerve Techniques<|im_end|>"},
            {"role": "user", "content": f"<|im_start|>user\n```{clean}```\n\n{ptitle}<|im_end|>"},
        ]
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
            json={
                "model": model,
                "messages": messages
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            print(f"Unexpected API response format: {result}")
            return None
    except requests.RequestException as e:
        print(f"Error generating title: {str(e)}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding API response: {response.text}")
        return None

def get_unique_title(Title, clean, used_titles, ptitle, max_attempts=3):
    original_title = Title
    for attempt in range(max_attempts):
        if Title not in used_titles:
            used_titles.add(Title)
            return Title, None
        else:
            generated_title = generate_title(clean, ptitle)
            if generated_title and generated_title not in used_titles:
                used_titles.add(generated_title)
                return generated_title, generated_title
            elif generated_title:
                Title = generated_title  # Try this new title in the next iteration
    
    # If we've exhausted all attempts, use a fallback title
    fallback_title = f"{original_title} (version {len([t for t in used_titles if t.startswith(original_title)])})"
    used_titles.add(fallback_title)
    print(f"Title generation failed after {max_attempts} attempts. Using fallback title: {fallback_title}")
    return fallback_title, fallback_title

def make_api_call(clean, prompt):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            messages = [
                {"role": "system", "content": f"<|im_start|>system\nYou are Hermes, an assistand who demonstrates expertise in meticulously documenting and analyzing academic texts, ensuring that every nuance and detail is captured with precision.<|im_end|>"},
                {"role": "user", "content": f"<|im_start|>user\n```It takes 1,836 electrons to equal the mass of one proton, so for most purposes we can disregard their mass. A person who weighs 64 kg (140 lb) contains less than 24 g (1 oz) of electrons. This hardly means that we can ignore electrons, however. They determine the chemical properties of an atom, governing what molecules can exist and what chemical reactions can occur. The number of elec - trons equals the number of protons, so their charges cancel each other and an atom is electrically neutral.Electrons swarm about the nucleus in concentric regions  called electron shells (energy levels). The more energy an elec - tron has, the farther away from the nucleus its orbit lies. Each shell holds a limited number of electrons. The elements known to date have up to seven electron shells, but those ordinarily involved in human physiology don’t exceed four. Electrons of the outermost shell, called valence electrons, determine the chemical bonding properties of an atom. Illustrations of atoms greatly understate the distances between their nuclei and electrons in order to fit the page. If you imagine the nucleus of an atom to be the size of a bas - ketball, its nearest electron would be about 48 km (30 mi.) away. 2.1c Isotopes and Radioactivity Dalton believed that every atom of an element was identical. We now know, however, that all elements have varieties called isotopes, 2 which differ from one another only in number of neu - trons and therefore in atomic mass. Hydrogen atoms, for example, have only one proton. In the most common isotope, symbolized  1H, that’s all there is to the nucleus. Hydrogen has two other FIGURE 2.1  Models of Atomic Structure. (a) The Bohr planetary  model of carbon, with electrons in two concentric energy levels  (shells), the higher-energy electrons farther from the nucleus. (b) The Bohr model of sodium, with a third electron shell. (c) The more realistic quantum mechanical model of carbon, in which electrons are depicted only by their probability of being in a given place at a given time, in shells separated by clear zones (nodes) of low to zero probability. First energy level Carbon (C) 6p+, 6e–,6n0 Atomic number = 6 Atomic mass = 12 (a) (b) (c)Sodium (Na) 11p+, 11e–, 12n0 Atomic number = 11 Atomic mass = 23Third energy level = Proton (p+)Key = Neutron (n0) = Electron (e–)Nucleus NodesElectron clouds 1a = not; tom  = cut2iso = same; top  = place (same position in the periodic table) isotopes, however: deuterium (2H) with one proton and one neu- tron, and tritium (3H) with one proton and two neutrons (fig. 2.3). Over 99 percent of carbon atoms have an atomic mass of 12 (6p+, 6n0)  and are called carbon-12 (12C), but a small percentage of carbon  atoms are 13C, with seven neutrons, and 14C, with eight. Despite  their differences in neutrons, however, all isotopes of a given ele - ment behave the same chemically. Deuterium (2H), for example,  reacts with oxygen the same way 1H does to produce water. The atomic weight (relative atomic mass)  of an element ac - counts for the fact that an element is a mixture of isotopes. If all  carbon were 12C, the atomic weight of carbon would be the same  as its atomic mass, 12.000. But since a sample of carbon also con - tains small amounts of the heavier isotopes 13C and 14C, the atomic  weight is slightly higher, 12.011.Although different isotopes of an element exhibit identi - cal chemical behavior, they differ in physical behavior. Many of them are unstable and decay (break down) to more stable isotopes  by giving off radiation. Unstable isotopes are therefore called   radioisotopes,  and the process of decay is called radioactivity   (see Deeper Insight 2.1). Every element has at least one radioiso - tope. Oxygen, for example, has three stable isotopes and five radio-isotopes. All of us contain radioisotopes such as  14C and 40K—that  is, we are all mildly radioactive. High-energy radiation, such as that emitted by radioisotopes,  ejects electrons from other atoms, converting atoms to ions; thus, it is called ionizing radiation. It destroys molecules and produces  dangerous free radicals and ions in human tissues. In high doses,   ionizing radiation is quickly fatal. In lower doses, it can be muta- genic (causing mutations in DNA) and carcinogenic  (triggering  cancer as a result of mutation). Examples of ionizing radiation include ultraviolet rays,   X-rays, and three kinds of radiation produced by nuclear decay: alpha (α) particles, beta (β) particles,  and gamma (γ) rays. An  alpha particle consists of two protons and two neutrons  ( equivalent to a helium nucleus), and a beta particle is a free  electron. Alpha particles are too large to penetrate the skin, and beta particles penetrate only a few millimeters. They’re relatively  harmless when emitted by sources outside the body, but very dangerous when emitted by radioisotopes that have gotten into the body. Strontium-90 ( 90Sr), for example, has been released by  nuclear accidents and the atmospheric testing of nuclear weapons FIGURE 2.3  Isotopes of Hydrogen. The three isotopes differ  only in the number of neutrons present. Hydrogen (1H) (1p+, 0n0, 1e–)Tritium (3H) (1p+, 2n0, 1e–)Deuterium (2H) (1p+, 1n0, 1e–)DEEPER INSIGHT 2.1 MEDICAL HISTORY Radiation and Madame Curie In 1896, French scientist Henri Becquerel (1852–1908) discovered that  uranium darkened photographic plates through several thick layers of paper. Marie Curie (1867–1934) and her husband Pierre Curie (1859–1906) discovered that polonium and radium did likewise. Marie coined the term radioactivity for the emission of energy by these elements. Becquerel and the Curies shared a Nobel Prize in 1903 for this discovery. Marie Curie (fig. 2.2) was not only the first woman in the world to  receive a Nobel Prize, but also the first woman in France to receive a Ph.D. She received a second Nobel Prize in 1911 for further work in radiation. Curie crusaded to train women for careers in science, and in World War I, she and her daughter, Irène Joliot-Curie (1897–1956), trained physicians in the use of X-ray machines. Marie pioneered radia-tion therapy for breast and uterine cancer. In the wake of such discoveries, radium was regarded as a wonder  drug. Unaware of its danger, people drank radium tonics and flocked to health spas to bathe in radium-enriched waters. Marie herself suffered extensive damage to her hands from handling radioactive minerals and died of radiation poisoning at age 67. The following year, Irène and her husband, Frédéric Joliot (1900–1958), were awarded a Nobel Prize for work in artificial radioactivity and synthetic radioisotopes. Apparently also a martyr to her science, Irène died of leukemia, possibly induced by radiation exposure. FIGURE 2.2  Marie Curie (1867–1934). This portrait was made  in 1911, when Curie received her second Nobel Prize. Library of Congress Prints and Photographs Division [LC-DIG-ggbain-06354] in the 1950s and 1960s. It settles onto pastures and contaminates  cow’s milk. In the body, it behaves chemically like calcium, be - coming incorporated into the bones, where it emits beta particles for years. Uranium and plutonium emit gamma rays. Because of  their high penetrating power, these rays are very dangerous even when emitted by sources outside the body. Each radioisotope has a characteristic physical half-life,   the time required for 50 percent of its atoms to decay to a more stable isotope.```\n\n{prompt}<|im_end|>"},
                {"role": "assistant", "content": f"<|im_start|>assistant\n**Electrons and Atomic Structure**\n\n- Electrons have negligible mass compared to protons (1,836 electrons = 1 proton)\n- A 64 kg person contains less than 24 g of electrons\n- Electrons are crucial for:\n- Determining chemical properties of atoms\n- Governing molecule formation and chemical reactions\n- Number of electrons equals number of protons in an atom, making it electrically neutral\n- **Electron shells** (energy levels):\n- Concentric regions around the nucleus\n- Higher energy electrons orbit farther from nucleus\n- Each shell has a limited electron capacity\n- Up to seven shells possible, but human physiology involves up to four\n- **Valence electrons**: Outermost shell electrons determining chemical bonding properties\n- Atomic scale: If nucleus wa basketball-sized, nearest electron would be 48 km away\n\n**Isotopes and Radioactivity**\n\n- **Isotopes**: Varieties of an element differing in neutron count and atomic mass\n- Hydrogen isotopes:\n- 1H (most common): 1 proton\n- **Deuterium** (2H): 1 proton, 1 neutron\n- **Tritium** (3H): 1 proton, 2 neutrons\n- Carbon isotopes: 12C (most common), 13C, 14C\n- All isotopes of an element behave identically chemically\n- **Atomic weight** (relative atomic mass): Accounts for isotope mixture in an element\n- **Radioisotopes**: Unstable isotopes that decay by emitting radiation\n- **Radioactivity**: Process of radioisotope decay\n- Every element has at least one radioisotope\n- Humans contain radiisotopes like 14C and 40K\n\n**Ionizing Radiation**\n\n- High-energy radiation ejecting electrons from atoms\n- Effects:\n- Destroys molecules\n- Produces dangerous free radicals and ions in tissues\n- Can be mutagenic and carcinogenic\n- Types:\n- Ultraviolet rays\n- X-rays\n- Alpha (α) particles: 2 protons, 2 neutrons\n- Beta (β) particles: Free electrons\n- Gamma (γ) rays\n- Penetration power:\n- Alpha particles: Cannot penetrate skin\n- Beta particles: Penetrate a few millimeters\n- Gamma rays: High penetrating power, dangerous even from external sources\n- Dangers of internal radioisotopes (e.g., Strntium-90)\n\n**Medical History: Radiation and Madame Curie**\n\n- **Henri Becquerel** discovered uranium's radiation properties in 1896\n- **Marie Curie** and **Pierre Curie** discovered polonium and radium's radioactivity\n- Marie Curie:\n- Coined the term “radioactivity“\n- First woman to receive a Nobel Prize (1903, shared with Becquerel and Pierre)\n- First woman in France to receive a Ph.D.\n- Received second Nobel Prize in 1911\n- Pioneered radiation therapy for breast and uterine cancer\n- Died of radiation poisoning at 67\n- **Irène Joliot-Curie** (Marie's daughter) and **Frédéric Joliot**:\n- Awarded Nobel Prize for work in artificial radioactivity and synthetic radioisotopes\n- Irène died of leukemia possibly due to radiation exposure\n\n**Radioisotope Properties**\n\n- **Physical half-life**: Time for 50 percent of atoms to decay to a more stable isotope\n- Each radioisotope has a characteristic half-life<|im_end|>"},
                {"role": "user", "content": f"<|im_start|>user\n```{clean}```\n\n{prompt}<|im_end|>"},
            ]

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                },
                json={
                    "model": model,
                    "messages": messages
                },
                timeout=90
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                print(f"Unexpected API response format. Full response:\n{json.dumps(result, indent=2)}")
                return None

        except requests.RequestException as e:
            print(f"Error in API call (attempt {attempt + 1}): {str(e)}")
            print(f"Full response:\n{response.text}")
        except json.JSONDecodeError as e:
            print(f"Error decoding API response (attempt {attempt + 1}): {str(e)}")
            print(f"Full response:\n{response.text}")
        except KeyError as e:
            print(f"KeyError in API response (attempt {attempt + 1}): {str(e)}")
            print(f"Full response:\n{json.dumps(response.json(), indent=2)}")
        
        if attempt < max_retries - 1:
            print("Retrying in 5 seconds...")
            time.sleep(5)
        else:
            print("Max retries reached. Skipping this API call.")
    
    return None

def process_file(input_file):
    prompt = "Write comprehensive bulleted notes on the provided text."
    ptitle = "write a fewer than 20 words to concisely describe this passage."

    # Extract filename without extension
    filename = os.path.basename(input_file)
    filename_no_ext, _ = os.path.splitext(filename)

    # Markdown file
    model_name = model.split("/")[-1]
    markdown_file = f"{filename_no_ext}_{model_name}.md"
    with open(markdown_file, "w") as f:
        f.write(f"# {filename_no_ext}\n\n")
        f.write(f"{prompt}\n\n")
        f.write(f"## {model}\n\n")
        
        # Write model information
        f.write("### Model Information\n\n")
        f.write(f"- Model: {model}\n")
        f.write("- API: OpenRouter\n\n")

    # CSV file
    csv_file = f"{filename_no_ext}_summ.csv"
    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Text", model, "Time", "Len"])

    # Initialize a set to store used titles
    used_titles = set()

    # Loop through each line in the input CSV file
    with open(input_file, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for i, row in enumerate(reader, 1):
            print(f"Processing row {i}...", end='\r')
            Title, Text, _ = row  # Ignore the Character Count column
            clean = re.sub(r"!", ".", re.sub(r"%", " percent", Text))

            # Record the start time
            start_time = time.time()

            # Make the API call
            output = make_api_call(clean, prompt)

            if output is None:
                continue  # Skip this iteration if the API call failed

            # Record the end time
            end_time = time.time()

            # Calculate the processing time
            elapsed_time = end_time - start_time

            # Check if the title has '|'
            if "|" in Title:
                # Split the title by '|'
                title_parts = Title.split("|")
                # The first part before '|' is the h2 title
                h2_title = title_parts[0]
                # The rest of the parts after the last '|' are joined together to form the h3 title
                h3_title = "|".join(title_parts[1:])
                
                unique_title, generated_title = get_unique_title(Title, clean, used_titles, ptitle)
                if generated_title:
                    heading = f"#### {unique_title}"
                else:
                    heading = f"## {h2_title}\n### {h3_title}"
            else:
                unique_title, generated_title = get_unique_title(Title, clean, used_titles, ptitle)
                heading = f"### {unique_title}" if not generated_title else f"#### {unique_title}"

            # Append the output to the markdown file
            with open(markdown_file, "a") as f:
                f.write(f"{heading}\n\n")
                f.write(f"{output}\n\n")

            # Format Input + Output for CSV Format
            cout = re.sub(r"\n", "\\\\n", output)
            size = len(cout)

            # Use generated_title if available, otherwise use the original Title
            csv_title = generated_title if generated_title else Title

            # Escape double quotes in csv_title, Text, and cout
            csv_title = re.sub(r'"', '""', csv_title)
            Text = re.sub(r'"', '""', Text)
            cout = re.sub(r'"', '""', cout)

            # Write to CSV file
            with open(csv_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([csv_title, Text, cout, elapsed_time, size])

            # Wait for 2 seconds before the next API call
            time.sleep(2)
        print("\nProcessing complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sum.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    process_file(input_file)
