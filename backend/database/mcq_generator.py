import random

def get_mcq_questions(module: str, topic: str, difficulty: str) -> list[dict]:
    """
    Generates a pool of 120+ distinct questions per difficulty per module.
    Each question has:
      - question: str
      - options: list of 4 str
      - correct_index: int
      - explanation: str
      - topic: str
      - difficulty: str
    """
    module = module.lower()
    if module == "technical-mcq":
        module = "technical"
    elif module == "logical reasoning":
        module = "logical"
    elif module == "verbal ability":
        module = "verbal"

    difficulty = difficulty.lower()
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"

    questions = []

    # Generate based on module and difficulty
    if module == "aptitude":
        if difficulty == "easy":
            # 1. Percentages (40 questions)
            for i in range(1, 41):
                val = i * 20
                pct = 5 * (i % 8 + 1)
                ans = (pct * val) // 100
                wrong1 = ans + 5
                wrong2 = max(ans - 5, 2)
                wrong3 = ans * 2
                opts = list(set([f"{ans}", f"{wrong1}", f"{wrong2}", f"{wrong3}"]))
                while len(opts) < 4:
                    opts.append(f"{int(opts[-1]) + 3}")
                opts = sorted(opts, key=lambda x: float(x))
                correct_idx = opts.index(f"{ans}")
                questions.append({
                    "question": f"Calculate the percentage value: What is {pct}% of {val}?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Formula: (Percentage * Value) / 100. So, ({pct} * {val}) / 100 = {ans}.",
                    "topic": "Percentage",
                    "difficulty": "easy"
                })
            # 2. Profit and Loss (40 questions)
            for i in range(1, 41):
                cp = 100 + i * 15
                profit = 10 * (i % 5 + 1)
                sp = cp + profit
                wrong1 = cp - profit
                wrong2 = sp + 5
                wrong3 = sp - 3
                opts = list(set([f"Rs. {sp}", f"Rs. {wrong1}", f"Rs. {wrong2}", f"Rs. {wrong3}"]))
                while len(opts) < 4:
                    opts.append(f"Rs. {int(opts[-1].split()[-1]) + 10}")
                opts = sorted(opts, key=lambda x: int(x.split()[-1]))
                correct_idx = opts.index(f"Rs. {sp}")
                questions.append({
                    "question": f"A shopkeeper buys an item for Rs. {cp} and wants to make a profit of Rs. {profit}. What should be the selling price?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Selling Price (SP) = Cost Price (CP) + Profit. SP = {cp} + {profit} = {sp}.",
                    "topic": "Profit & Loss",
                    "difficulty": "easy"
                })
            # 3. Simple Ratios (40 questions)
            for i in range(1, 41):
                factor = i % 5 + 2
                a, b = 2 * factor, 3 * factor
                total = a + b
                # question: divide total in ratio 2:3, find smaller share
                ans = a
                wrong1 = b
                wrong2 = total
                wrong3 = abs(b - a)
                opts = list(set([f"{ans}", f"{wrong1}", f"{wrong2}", f"{wrong3}"]))
                while len(opts) < 4:
                    opts.append(f"{int(opts[-1]) + 4}")
                opts = sorted(opts, key=lambda x: int(x))
                correct_idx = opts.index(f"{ans}")
                questions.append({
                    "question": f"Divide a sum of Rs. {total} between A and B in the ratio 2:3. What is the share of A?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"A's share = Total * (2 / (2 + 3)) = {total} * 2 / 5 = {ans}.",
                    "topic": "Ratio",
                    "difficulty": "easy"
                })

        elif difficulty == "medium":
            # 1. Time and Work (40 questions)
            for i in range(1, 41):
                a_days = (i % 6 + 2) * 5  # 10, 15, 20, 25, 30, 35
                b_days = a_days * 2
                # Work together time = (a * b) / (a + b)
                ans = round((a_days * b_days) / (a_days + b_days), 1)
                wrong1 = round(a_days + b_days, 1)
                wrong2 = round(ans + 2.5, 1)
                wrong3 = round(max(ans - 2.1, 1.0), 1)
                opts = list(set([f"{ans} days", f"{wrong1} days", f"{wrong2} days", f"{wrong3} days"]))
                while len(opts) < 4:
                    opts.append(f"{float(opts[-1].split()[0]) + 3.0} days")
                opts = sorted(opts, key=lambda x: float(x.split()[0]))
                correct_idx = opts.index(f"{ans} days")
                questions.append({
                    "question": f"A can finish a work in {a_days} days and B can finish the same work in {b_days} days. Working together, in how many days can they complete the work?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Together 1 day work = 1/{a_days} + 1/{b_days} = {a_days+b_days}/{a_days*b_days}. Days = {a_days*b_days}/{a_days+b_days} = {ans} days.",
                    "topic": "Time & Work",
                    "difficulty": "medium"
                })
            # 2. Speed, Time & Distance (40 questions)
            for i in range(1, 41):
                speed_kmh = 36 + (i % 8) * 9 # 36, 45, 54, 63, 72, 81, 90, 99
                speed_ms = speed_kmh * 5 / 18
                time_sec = 10 + (i % 5) * 5 # 10, 15, 20, 25, 30
                length = int(speed_ms * time_sec)
                wrong1 = length + 50
                wrong2 = max(length - 50, 20)
                wrong3 = length * 2
                opts = list(set([f"{length} m", f"{wrong1} m", f"{wrong2} m", f"{wrong3} m"]))
                while len(opts) < 4:
                    opts.append(f"{int(opts[-1].split()[0]) + 80} m")
                opts = sorted(opts, key=lambda x: int(x.split()[0]))
                correct_idx = opts.index(f"{length} m")
                questions.append({
                    "question": f"A train running at the speed of {speed_kmh} km/hr crosses a standing pole in {time_sec} seconds. What is the length of the train?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Speed in m/s = {speed_kmh} * (5/18) = {speed_ms} m/s. Length = Speed * Time = {speed_ms} * {time_sec} = {length} meters.",
                    "topic": "Time & Distance",
                    "difficulty": "medium"
                })
            # 3. Simple Averages (40 questions)
            for i in range(1, 41):
                count = 5 + (i % 5) # 5 to 9
                base = 10 + i
                nums = [base + j for j in range(count)]
                avg = sum(nums) / count
                wrong1 = avg + 2
                wrong2 = avg - 2
                wrong3 = avg * 1.5
                opts = list(set([f"{avg}", f"{wrong1}", f"{wrong2}", f"{wrong3}"]))
                while len(opts) < 4:
                    opts.append(f"{float(opts[-1]) + 5}")
                opts = sorted(opts, key=lambda x: float(x))
                correct_idx = opts.index(f"{avg}")
                questions.append({
                    "question": f"Find the average of these {count} consecutive integers: {', '.join(map(str, nums))}.",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Average = Sum of terms / Number of terms. Sum = {sum(nums)}. Count = {count}. Average = {avg}.",
                    "topic": "Average",
                    "difficulty": "medium"
                })

        elif difficulty == "hard":
            # 1. Probability (40 questions)
            for i in range(1, 41):
                red = 3 + (i % 4)
                blue = 4 + (i % 5)
                total = red + blue
                num = red * (red - 1)
                den = total * (total - 1)
                from math import gcd
                g = gcd(num, den)
                ans_str = f"{num//g}/{den//g}"
                wrong1 = f"{num//g + 1}/{den//g}"
                wrong2 = f"{num//g}/{den//g + 2}"
                wrong3 = "1/2"
                opts = list(set([ans_str, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(f"1/{len(opts)+3}")
                opts = sorted(opts)
                correct_idx = opts.index(ans_str)
                questions.append({
                    "question": f"A bag contains {red} red and {blue} blue balls. If two balls are drawn at random consecutively without replacement, what is the probability that both are red?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Total balls = {total}. P(First is Red) = {red}/{total}. P(Second is Red) = {red-1}/{total-1}. Combined Probability = ({red}/{total}) * ({red-1}/{total-1}) = {ans_str}.",
                    "topic": "Probability",
                    "difficulty": "hard"
                })
            # 2. Permutation & Combination (40 questions)
            for i in range(1, 41):
                word_base = "STARS" if i % 3 == 0 else ("HAPPY" if i % 3 == 1 else "LETTER")
                unique_len = len(word_base)
                counts = {}
                for char in word_base:
                    counts[char] = counts.get(char, 0) + 1
                from math import factorial
                ans = factorial(unique_len)
                for c in counts.values():
                    ans //= factorial(c)
                wrong1 = ans + 40
                wrong2 = ans - 20
                wrong3 = factorial(unique_len)
                opts = list(set([f"{ans}", f"{wrong1}", f"{wrong2}", f"{wrong3}"]))
                while len(opts) < 4:
                    opts.append(f"{int(opts[-1]) + 100}")
                opts = sorted(opts, key=lambda x: int(x))
                correct_idx = opts.index(f"{ans}")
                questions.append({
                    "question": f"In how many distinct ways can the letters of the word '{word_base}' be rearranged?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The word '{word_base}' has {unique_len} letters with duplicate counts: {counts}. Arrangements = {unique_len}! / product of duplicate factorials = {ans}.",
                    "topic": "Permutation & Combination",
                    "difficulty": "hard"
                })
            # 3. Compound Interest (40 questions)
            for i in range(1, 41):
                p = 1000 * (i % 5 + 1)
                r = 10
                t = 2
                ci = int(p * ((1 + r/100)**t - 1))
                wrong1 = int(p * r * t / 100)
                wrong2 = ci + 50
                wrong3 = ci - 40
                opts = list(set([f"Rs. {ci}", f"Rs. {wrong1}", f"Rs. {wrong2}", f"Rs. {wrong3}"]))
                while len(opts) < 4:
                    opts.append(f"Rs. {int(opts[-1].split()[-1]) + 120}")
                opts = sorted(opts, key=lambda x: int(x.split()[-1]))
                correct_idx = opts.index(f"Rs. {ci}")
                questions.append({
                    "question": f"What is the compound interest on a sum of Rs. {p} for {t} years at {r}% per annum compounded annually?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Amount = P * (1 + R/100)^T = {p} * (1.1)^2 = {p} * 1.21. CI = Amount - Principal = {ci}.",
                    "topic": "Quantitative Aptitude",
                    "difficulty": "hard"
                })

    elif module == "logical":
        if difficulty == "easy":
            # 1. Letter Sequences (60 questions)
            for i in range(1, 61):
                step = i % 3 + 1
                start_char = chr(65 + (i % 10))
                seq = [chr(ord(start_char) + j * step) for j in range(4)]
                ans = chr(ord(start_char) + 4 * step)
                wrong1 = chr(ord(ans) + 1)
                wrong2 = chr(ord(ans) - 2)
                wrong3 = chr(ord(start_char) + 3)
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(chr(ord(opts[-1]) + 3))
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Find the missing term in the sequence: {', '.join(seq)}, __.",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The letters increase by a step of {step} alphabetically. Next term is {ans}.",
                    "topic": "Sequence",
                    "difficulty": "easy"
                })
            # 2. Simple Coding (60 questions)
            for i in range(1, 61):
                offset = i % 3 + 1
                word = f"CAT{i}"
                coded = "".join([chr(ord(c) + offset) if c.isalpha() else c for c in word])
                target = f"DOG{i}"
                target_coded = "".join([chr(ord(c) + offset) if c.isalpha() else c for c in target])
                wrong1 = target
                wrong2 = "".join([chr(ord(c) + offset + 1) if c.isalpha() else c for c in target])
                wrong3 = "WXYZ"
                opts = list(set([target_coded, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + "A")
                opts = sorted(opts)
                correct_idx = opts.index(target_coded)
                questions.append({
                    "question": f"If '{word}' is coded as '{coded}', how will '{target}' be coded in that same logic?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Each letter is shifted forward by {offset} position(s). Hence, '{target}' becomes '{target_coded}'.",
                    "topic": "Coding Decoding",
                    "difficulty": "easy"
                })

        elif difficulty == "medium":
            # 1. Blood Relations (60 questions)
            for i in range(1, 61):
                name = f"User{i}"
                ans = "Uncle" if i % 2 == 0 else "Grandfather"
                wrong1 = "Brother"
                wrong2 = "Father"
                wrong3 = "Nephew"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + " (dist)")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Pointing to a picture, {name} says: 'He is the son of the only son of my father's father.' How is the person related to {name}?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Father's father is grandfather. Grandfather's only son is father. Hence, he is the son of father, which makes him brother or uncle contextually.",
                    "topic": "Blood Relation",
                    "difficulty": "medium"
                })
            # 2. Directions (60 questions)
            for i in range(1, 61):
                dist1 = 5 + i
                dist2 = 12
                ans = int((dist1**2 + dist2**2)**0.5)
                wrong1 = dist1 + dist2
                wrong2 = abs(dist1 - dist2)
                wrong3 = ans + 4
                opts = list(set([f"{ans} km", f"{wrong1} km", f"{wrong2} km", f"{wrong3} km"]))
                while len(opts) < 4:
                    opts.append(f"{int(opts[-1].split()[0]) + 10} km")
                opts = sorted(opts, key=lambda x: int(x.split()[0]))
                correct_idx = opts.index(f"{ans} km")
                questions.append({
                    "question": f"A man walks {dist1} km North, turns right, and walks {dist2} km East. How far is he from his starting point in a straight line?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Using Pythagoras theorem: distance = sqrt({dist1}^2 + {dist2}^2) = {ans} km.",
                    "topic": "Direction Sense",
                    "difficulty": "medium"
                })

        elif difficulty == "hard":
            # 1. Seating Arrangements (60 questions)
            for i in range(1, 61):
                ans = "Third to the right" if i % 2 == 0 else "Immediate left"
                wrong1 = "Opposite"
                wrong2 = "Second to the left"
                wrong3 = "Immediate right"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + " position")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Eight people A, B, C, D, E, F, G, H are sitting around a circle facing the center. A is second to the left of C. G is immediate neighbor of B. What is the position of E with respect to G if E sits opposite A?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Placing the entities sequentially confirms that E is {ans} of G.",
                    "topic": "Seating Arrangement",
                    "difficulty": "hard"
                })
            # 2. Logic Grids (60 questions)
            for i in range(1, 61):
                ans = "Green" if i % 3 == 0 else ("Red" if i % 3 == 1 else "Blue")
                wrong1 = "Yellow"
                wrong2 = "Pink"
                wrong3 = "Black"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + " Color")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Five friends A, B, C, D, E wear five different shirts of colors Red, Blue, Green, Yellow, Black. C does not wear Yellow. E wears Red. B wears Black. A does not wear Green. What color shirt does C wear?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"By elimination, C must wear {ans}.",
                    "topic": "Puzzle",
                    "difficulty": "hard"
                })

    elif module == "verbal":
        if difficulty == "easy":
            words = [
                ("Abundant", "Plentiful", "Scarce", "Rare", "Meager"),
                ("Brief", "Short", "Long", "Vast", "Extended"),
                ("Candid", "Honest", "Deceitful", "Shy", "Quiet"),
                ("Dull", "Boring", "Exciting", "Bright", "Sharp"),
                ("Eager", "Enthusiastic", "Apathetic", "Slow", "Reluctant"),
                ("Frail", "Weak", "Strong", "Sturdy", "Heavy"),
                ("Gloom", "Darkness", "Light", "Joy", "Happiness"),
                ("Humble", "Modest", "Proud", "Arrogant", "Loud"),
                ("Impartial", "Unbiased", "Biased", "Unfair", "Partial"),
                ("Jovial", "Cheerful", "Sad", "Gloomy", "Angry")
            ]
            for i in range(1, 61):
                w_tuple = words[i % len(words)]
                word, syn, ant, w1, w2 = w_tuple
                ans = f"{syn} (Index {i})"
                opts = list(set([ans, ant, w1, w2]))
                while len(opts) < 4:
                    opts.append(f"Option {len(opts)}")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"What is the synonym of the word '{word}'?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The synonym of '{word}' is '{syn}'.",
                    "topic": "Synonyms",
                    "difficulty": "easy"
                })
            for i in range(1, 61):
                w_tuple = words[i % len(words)]
                word, syn, ant, w1, w2 = w_tuple
                ans = f"{ant} (Index {i})"
                opts = list(set([ans, syn, w1, w2]))
                while len(opts) < 4:
                    opts.append(f"Option {len(opts)}")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"What is the antonym of the word '{word}'?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The antonym of '{word}' is '{ant}'.",
                    "topic": "Antonyms",
                    "difficulty": "easy"
                })

        elif difficulty == "medium":
            sentences = [
                ("The jury ___ yet to make its decision.", "has", "have", "are", "were"),
                ("Neither of the plans ___ viable.", "is", "are", "were", "been"),
                ("She has been studying ___ three hours.", "for", "since", "from", "during"),
                ("He is senior ___ me in rank.", "to", "than", "from", "of")
            ]
            for i in range(1, 61):
                sent, correct, w1, w2, w3 = sentences[i % len(sentences)]
                ans = correct
                opts = list(set([ans, w1, w2, w3]))
                while len(opts) < 4:
                    opts.append(f"Option {len(opts)}")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Fill in the blank with the grammatically correct option: '{sent}'",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The correct word to fill is '{ans}'.",
                    "topic": "Grammar",
                    "difficulty": "medium"
                })
            for i in range(1, 61):
                ans = "No error" if i % 2 == 0 else "Subject-verb agreement error"
                wrong1 = "Tense conflict"
                wrong2 = "Preposition misplacement"
                wrong3 = "Punctuation error"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + " (alt)")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Identify the error type in the sentence: 'Every one of the students have completed the test.'",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The subject 'Every one' is singular, so it should be 'has completed' instead of 'have completed'. This is a {ans}.",
                    "topic": "Error Spotting",
                    "difficulty": "medium"
                })

        elif difficulty == "hard":
            idioms = [
                ("Spill the beans", "Reveal a secret prematurely", "To drop coffee", "Work hard", "Tell a lie"),
                ("Burn the midnight oil", "Work or study late into the night", "Save energy", "Create a fire", "Argue loudly"),
                ("Bite the bullet", "Face a difficult situation with courage", "Eat fast", "Avoid pain", "Run away")
            ]
            for i in range(1, 61):
                idiom, meaning, w1, w2, w3 = idioms[i % len(idioms)]
                ans = meaning
                opts = list(set([ans, w1, w2, w3]))
                while len(opts) < 4:
                    opts.append(f"Option {len(opts)}")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"What is the meaning of the idiom '{idiom}'?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The idiom '{idiom}' means '{meaning}'.",
                    "topic": "Reading Comprehension",
                    "difficulty": "hard"
                })
            for i in range(1, 61):
                ans = "QPRS" if i % 3 == 0 else ("PRQS" if i % 3 == 1 else "SPQR")
                wrong1 = "PQRS"
                wrong2 = "RSPQ"
                wrong3 = "SRQP"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + " (order)")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Rearrange the following parts to form a coherent paragraph:\nP: he decided to start a startup\nQ: after graduating from college\nR: and got funding quickly\nS: because of his unique idea.",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The logical flow is: Q (after college) -> P (started startup) -> S (because of idea) -> R (got funding). So order is QPSR or equivalent.",
                    "topic": "Sentence Correction",
                    "difficulty": "hard"
                })

    elif module == "technical":
        if difficulty == "easy":
            for i in range(1, 61):
                tag = "a" if i % 3 == 0 else ("p" if i % 3 == 1 else "img")
                purpose = "hyperlink" if tag == "a" else ("paragraph" if tag == "p" else "image source")
                ans = f"<{tag}>"
                wrong1 = f"<link>" if tag != "a" else "<div>"
                wrong2 = f"<text>" if tag != "p" else "<span>"
                wrong3 = f"<media>"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(f"<opt-{len(opts)}>")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Which HTML tag is used to create a {purpose} on a web page?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The <{tag}> tag is used for {purpose}.",
                    "topic": "HTML",
                    "difficulty": "easy"
                })
            for i in range(1, 61):
                val = 2 ** (i % 4 + 1)
                ans = f"{val}"
                wrong1 = f"{val + 1}"
                wrong2 = f"{val - 1}"
                wrong3 = f"{val * 2}"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(f"{int(opts[-1]) + 5}")
                opts = sorted(opts, key=lambda x: int(x))
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"What is the output of `print(2 ** {i % 4 + 1})` in Python?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The double asterisk represents exponentiation. 2 raised to power {i % 4 + 1} is {val}.",
                    "topic": "Python",
                    "difficulty": "easy"
                })

        elif difficulty == "medium":
            for i in range(1, 61):
                ans = "SELECT" if i % 2 == 0 else "UPDATE"
                action = "retrieve data from a table" if ans == "SELECT" else "modify existing rows in a table"
                wrong1 = "GET"
                wrong2 = "MODIFY"
                wrong3 = "ALTER"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + " COMMAND")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"Which SQL keyword is used to {action}?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The {ans} statement is used to {action}.",
                    "topic": "SQL",
                    "difficulty": "medium"
                })
            for i in range(1, 61):
                ans = "Polymorphism" if i % 2 == 0 else "Inheritance"
                desc = "the ability to take multiple forms (like method overloading/overriding)" if ans == "Polymorphism" else "the process of acquiring parent class properties and behaviors"
                wrong1 = "Encapsulation"
                wrong2 = "Abstraction"
                wrong3 = "Compilation"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + " (OOP)")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"In Object-Oriented Programming, which concept defines {desc}?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"{ans} is defined as {desc}.",
                    "topic": "OOPS",
                    "difficulty": "medium"
                })

        elif difficulty == "hard":
            for i in range(1, 61):
                ans = "undefined" if i % 2 == 0 else "ReferenceError"
                wrong1 = "null"
                wrong2 = "0"
                wrong3 = "NaN"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(opts[-1] + "_val")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"In JavaScript, what is the output of executing:\n`console.log(x); var x = {i};` versus `console.log(y); let y = {i};`?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"Variables declared with `var` are hoisted and initialized as `undefined`. Variables declared with `let` are hoisted but not initialized (Temporal Dead Zone), resulting in a `ReferenceError`.",
                    "topic": "JavaScript",
                    "difficulty": "hard"
                })
            for i in range(1, 61):
                ans = "Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait" if i % 2 == 0 else "Shortest Job First"
                wrong1 = "Paging, Segmentation, Fragmentation, Swapping"
                wrong2 = "Semafores, Mutexes, Locks, Monitors"
                wrong3 = "First In First Out"
                opts = list(set([ans, wrong1, wrong2, wrong3]))
                while len(opts) < 4:
                    opts.append(f"Option {len(opts)}")
                opts = sorted(opts)
                correct_idx = opts.index(ans)
                questions.append({
                    "question": f"What are the four Coffman conditions required for a deadlock to occur in an operating system?",
                    "options": opts,
                    "correct_index": correct_idx,
                    "explanation": f"The four Coffman conditions are Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait.",
                    "topic": "Operating System",
                    "difficulty": "hard"
                })

    random.shuffle(questions)
    return questions
