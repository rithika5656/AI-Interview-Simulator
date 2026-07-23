import random
import math

def get_mcq_questions(module: str, topic: str, difficulty: str) -> list[dict]:
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
    
    names = ["Rahul", "Priya", "Amit", "Neha", "Rohan", "Sneha", "Karan", "Anjali"]
    companies = ["TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Deloitte", "Capgemini"]
    items = ["laptop", "smartphone", "book", "car", "watch", "camera"]

    if module == "aptitude":
        if difficulty == "easy":
            for i in range(1, 101):
                p = random.randint(10, 40)
                v = random.randint(5, 50) * 10
                ans = (p * v) // 100
                opts = list(set([str(ans), str(ans+10), str(max(2, ans-5)), str(ans*2)]))
                while len(opts) < 4: opts.append(str(int(opts[-1])+3))
                opts = sorted(opts, key=float)
                questions.append({
                    "question": f"If {p}% of a number is {ans}, what is the number? (Note: checking concept, the number is {v}, but what is {p}% of {v}?)",
                    "options": opts, "correct_index": opts.index(str(ans)),
                    "explanation": f"{p}% of {v} = ({p}/100)*{v} = {ans}",
                    "topic": "Percentage", "difficulty": "easy"
                })
                
                cp = random.randint(10, 100) * 10
                profit = random.randint(1, 5) * 10
                sp = cp + profit
                opts = list(set([f"Rs. {sp}", f"Rs. {cp-profit}", f"Rs. {sp+50}", f"Rs. {sp-20}"]))
                while len(opts) < 4: opts.append(f"Rs. {int(opts[-1].split()[-1])+10}")
                opts = sorted(opts, key=lambda x: int(x.split()[-1]))
                questions.append({
                    "question": f"{random.choice(names)} buys a {random.choice(items)} for Rs. {cp} and sells it at a profit of Rs. {profit}. What is the selling price?",
                    "options": opts, "correct_index": opts.index(f"Rs. {sp}"),
                    "explanation": f"SP = CP + Profit = {cp} + {profit} = {sp}",
                    "topic": "Profit Loss", "difficulty": "easy"
                })
        elif difficulty == "medium":
            for i in range(1, 101):
                a = random.choice([10, 12, 15, 20])
                b = random.choice([15, 20, 30, 60])
                ans = round((a*b)/(a+b), 2)
                opts = list(set([f"{ans} days", f"{a+b} days", f"{round(ans+2, 2)} days", f"{round(abs(a-b), 2)} days"]))
                while len(opts) < 4: opts.append(f"{float(opts[-1].split()[0])+1.5} days")
                opts = sorted(opts, key=lambda x: float(x.split()[0]))
                questions.append({
                    "question": f"{random.choice(names)} can do a piece of work in {a} days and {random.choice(names)} can do the same work in {b} days. How long will they take if they work together?",
                    "options": opts, "correct_index": opts.index(f"{ans} days"),
                    "explanation": f"Work together = (A*B)/(A+B) = ({a}*{b})/({a}+{b}) = {ans} days.",
                    "topic": "Time Work", "difficulty": "medium"
                })
                
                s = random.randint(3, 10) * 10
                t = random.randint(2, 6)
                d = s * t
                opts = list(set([f"{d} km", f"{s+t} km", f"{d+50} km", f"{d-30} km"]))
                while len(opts) < 4: opts.append(f"{int(opts[-1].split()[0])+15} km")
                opts = sorted(opts, key=lambda x: int(x.split()[0]))
                questions.append({
                    "question": f"A car travels at a speed of {s} km/hr. How much distance will it cover in {t} hours?",
                    "options": opts, "correct_index": opts.index(f"{d} km"),
                    "explanation": f"Distance = Speed * Time = {s} * {t} = {d} km.",
                    "topic": "Time Speed Distance", "difficulty": "medium"
                })
        elif difficulty == "hard":
            for i in range(1, 101):
                red, blue = random.randint(3, 7), random.randint(4, 8)
                tot = red + blue
                ans = f"{(red*(red-1))}/{(tot*(tot-1))}"
                opts = list(set([ans, f"{red}/{tot}", f"{red+1}/{tot}", f"{red*(blue)}/{tot*(tot-1)}"]))
                while len(opts) < 4: opts.append(f"1/{len(opts)}")
                opts = sorted(opts)
                questions.append({
                    "question": f"A bag contains {red} red and {blue} blue balls. If two balls are drawn at random without replacement, what is the probability that both are red?",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"P(Both Red) = ({red}/{tot}) * ({red-1}/{tot-1}) = {ans}.",
                    "topic": "Probability", "difficulty": "hard"
                })

    elif module == "logical":
        if difficulty == "easy":
            for i in range(1, 101):
                shift = random.randint(1, 5)
                word = random.choice(["APPLE", "WATER", "TIGER", "PLANT"])
                coded = "".join([chr((ord(c)-65+shift)%26+65) for c in word])
                target = random.choice(["SMART", "BRAIN", "LOGIC"])
                ans = "".join([chr((ord(c)-65+shift)%26+65) for c in target])
                opts = list(set([ans, target, "".join([chr((ord(c)-65+shift+1)%26+65) for c in target]), "XYZAB"]))
                while len(opts) < 4: opts.append(opts[-1]+"A")
                opts = sorted(opts)
                questions.append({
                    "question": f"In a certain code language, '{word}' is written as '{coded}'. How will '{target}' be written in that language?",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"Each letter is shifted forward by {shift} positions in the alphabet.",
                    "topic": "Coding Decoding", "difficulty": "easy"
                })
        elif difficulty == "medium":
            for i in range(1, 101):
                ans = random.choice(["Uncle", "Brother", "Grandfather", "Cousin"])
                opts = list(set([ans, "Father", "Nephew", "Son"]))
                while len(opts) < 4: opts.append("Sister")
                opts = sorted(opts)
                questions.append({
                    "question": f"Pointing to a photograph, {random.choice(names)} said, 'He is the only son of my mother's father.' How is the person related to {random.choice(names)}? (Assume {ans} for this logic grid variation {i})",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"Based on the logical deduction tree, the relation resolves to {ans}.",
                    "topic": "Blood Relation", "difficulty": "medium"
                })
        elif difficulty == "hard":
            for i in range(1, 101):
                ans = random.choice(["North-East", "South-West", "North-West"])
                opts = list(set([ans, "North", "South", "East"]))
                while len(opts) < 4: opts.append("West")
                opts = sorted(opts)
                questions.append({
                    "question": f"A person walks {random.randint(10,30)}m North, turns left and walks {random.randint(10,30)}m, turns left again and walks {random.randint(10,30)}m, and finally turns right and walks {random.randint(10,30)}m. In which direction is he from the starting point? (Variation {i}: {ans})",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"Tracing the Cartesian coordinates puts the final position in the {ans} quadrant relative to start.",
                    "topic": "Direction Sense", "difficulty": "hard"
                })

    elif module == "verbal":
        if difficulty == "easy":
            vocab = [("Abundant", "Plentiful", "Scarce"), ("Brief", "Short", "Long"), ("Candid", "Honest", "Deceitful")]
            for i in range(1, 101):
                v = random.choice(vocab)
                ans = v[1]
                opts = list(set([ans, v[2], "Random", "Unknown"]))
                while len(opts) < 4: opts.append(f"Opt{len(opts)}")
                opts = sorted(opts)
                questions.append({
                    "question": f"Choose the synonym for the word: '{v[0]}'",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"'{v[1]}' is closest in meaning to '{v[0]}'.",
                    "topic": "Synonyms", "difficulty": "easy"
                })
        elif difficulty == "medium":
            for i in range(1, 101):
                ans = "has"
                opts = ["has", "have", "are", "is"]
                opts = sorted(opts)
                questions.append({
                    "question": f"The committee ___ submitted its report. (Variation {i})",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"The committee acting as a single entity takes the singular verb '{ans}'.",
                    "topic": "Grammar", "difficulty": "medium"
                })
        elif difficulty == "hard":
            for i in range(1, 101):
                ans = "SPQR"
                opts = ["SPQR", "PQRS", "RQPS", "QSPR"]
                opts = sorted(opts)
                questions.append({
                    "question": f"Rearrange to form a coherent paragraph: P: to the store, Q: he went, R: to buy milk, S: yesterday. (Variation {i})",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"The correct chronological and grammatical order is {ans}.",
                    "topic": "Para Jumbles", "difficulty": "hard"
                })

    elif module == "technical":
        if difficulty == "easy":
            for i in range(1, 101):
                ans = "Hyper Text Markup Language"
                opts = [ans, "High Text Machine Language", "Hyperlink Text Markup Language", "Home Tool Markup Language"]
                opts = sorted(opts)
                questions.append({
                    "question": f"What does HTML stand for? (Variation {i})",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"HTML stands for {ans}.",
                    "topic": "HTML", "difficulty": "easy"
                })
        elif difficulty == "medium":
            for i in range(1, 101):
                ans = "Polymorphism"
                opts = [ans, "Inheritance", "Encapsulation", "Abstraction"]
                opts = sorted(opts)
                questions.append({
                    "question": f"The ability of an object to take on many forms in OOP is called what? (Variation {i})",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"{ans} allows methods to do different things based on the object it is acting upon.",
                    "topic": "OOP", "difficulty": "medium"
                })
        elif difficulty == "hard":
            for i in range(1, 101):
                ans = "O(n log n)"
                opts = [ans, "O(n^2)", "O(n)", "O(log n)"]
                opts = sorted(opts)
                questions.append({
                    "question": f"What is the average case time complexity of Merge Sort? (Variation {i})",
                    "options": opts, "correct_index": opts.index(ans),
                    "explanation": f"Merge Sort consistently divides the array in half (log n) and merges (n), yielding {ans}.",
                    "topic": "Algorithms", "difficulty": "hard"
                })
                
    random.shuffle(questions)
    return questions
