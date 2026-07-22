"""High-quality multiple choice question bank for HireVision fallback and generation."""

QUESTION_BANK = {
    "aptitude": {
        "Quantitative Aptitude": [
            {
                "question": "A sum of money at compound interest amounts to Rs. 650 at the end of the first year and Rs. 676 at the end of the second year. What is the sum?",
                "options": ["Rs. 600", "Rs. 625", "Rs. 630", "Rs. 615"],
                "correct_index": 1,
                "explanation": "Let the sum be P. Rate = (26 / 650) * 100 = 4%. So, P * 1.04 = 650 => P = 625."
            },
            {
                "question": "The average of 20 numbers is zero. Of them, at most how many may be greater than zero?",
                "options": ["0", "1", "10", "19"],
                "correct_index": 3,
                "explanation": "To make the average 0, the sum of 20 numbers must be 0. Thus, 19 numbers can be positive (greater than 0) and the 20th number can be a negative number equal to the sum of the other 19."
            },
            {
                "question": "A and B invest in a business in the ratio 3:2. If 5% of the total profit goes to charity and A's share is Rs. 855, what is the total profit?",
                "options": ["Rs. 1425", "Rs. 1500", "Rs. 1537", "Rs. 1576"],
                "correct_index": 1,
                "explanation": "Let the total profit be Rs. 100. Profit after charity = Rs. 95. A's share = 95 * (3/5) = 57. If A's share is 57, total is 100. If A's share is 855, total is (100/57) * 855 = 1500."
            }
        ],
        "Number System": [
            {
                "question": "What is the unit digit in the product (3^65 * 6^59 * 7^71)?",
                "options": ["1", "2", "4", "6"],
                "correct_index": 2,
                "explanation": "Unit digit of 3^65 is 3 (cycle of 4). Unit digit of 6^59 is 6 (always 6). Unit digit of 7^71 is 3 (cycle of 4). So, 3 * 6 * 3 = 54, unit digit is 4."
            },
            {
                "question": "How many natural numbers between 17 and 80 are divisible by 6?",
                "options": ["10", "11", "12", "13"],
                "correct_index": 1,
                "explanation": "The numbers are 18, 24, ..., 78. This is an AP with a=18, d=6, l=78. n = ((78-18)/6) + 1 = 11. Let's list: 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78. Total is 11."
            },
            {
                "question": "Which of the following is a prime number?",
                "options": ["117", "187", "263", "289"],
                "correct_index": 2,
                "explanation": "117 = 9 * 13. 187 = 11 * 17. 289 = 17 * 17. 263 is prime because it is not divisible by any prime number less than its square root."
            }
        ],
        "Time & Work": [
            {
                "question": "A can do a work in 15 days and B in 20 days. If they work on it together for 4 days, then the fraction of the work that is left is:",
                "options": ["1/4", "1/10", "7/15", "8/15"],
                "correct_index": 3,
                "explanation": "A's 1 day work = 1/15, B's = 1/20. Together 1 day = (1/15 + 1/20) = 7/60. 4 days together = 28/60 = 7/15. Left work = 1 - 7/15 = 8/15."
            },
            {
                "question": "A is twice as good a workman as B and together they finish a piece of work in 18 days. In how many days will A alone finish the work?",
                "options": ["27 days", "30 days", "36 days", "54 days"],
                "correct_index": 0,
                "explanation": "Ratio of work of A and B = 2:1. Together 1 day work = 1/18. A's 1 day work = (1/18) * (2/3) = 1/27. So, A alone finishes in 27 days."
            },
            {
                "question": "If 12 men or 18 women can reap a field in 14 days, then in how many days can 8 men and 16 women reap the same field?",
                "options": ["5 days", "7 days", "9 days", "10 days"],
                "correct_index": 2,
                "explanation": "12 men = 18 women => 1 man = 1.5 women. 8 men + 16 women = (8 * 1.5) + 16 = 28 women. 18 women reap in 14 days. 28 women reap in (18 * 14) / 28 = 9 days."
            }
        ],
        "Time & Distance": [
            {
                "question": "A train passes a station platform in 36 seconds and a man standing on the platform in 20 seconds. If the speed of the train is 54 km/hr, what is the length of the platform?",
                "options": ["120 m", "240 m", "300 m", "360 m"],
                "correct_index": 1,
                "explanation": "Speed = 54 * (5/18) = 15 m/s. Length of train = 15 * 20 = 300 m. Let platform be L. (300 + L) / 15 = 36 => 300 + L = 540 => L = 240 m."
            },
            {
                "question": "Excluding stoppages, the speed of a bus is 54 km/hr and including stoppages, it is 45 km/hr. For how many minutes does the bus stop per hour?",
                "options": ["9 min", "10 min", "12 min", "15 min"],
                "correct_index": 1,
                "explanation": "Due to stoppages, it travels 9 km less per hour. Time taken to travel 9 km at 54 km/hr is (9 / 54) * 60 = 10 minutes."
            },
            {
                "question": "A person crosses a 600 m long street in 5 minutes. What is his speed in km/hr?",
                "options": ["3.6", "7.2", "8.4", "10"],
                "correct_index": 1,
                "explanation": "Speed = 600 m / (5 * 60) s = 2 m/s. In km/hr = 2 * (18/5) = 7.2 km/hr."
            }
        ],
        "Probability": [
            {
                "question": "In a box, there are 8 red, 7 blue and 6 green balls. One ball is picked up randomly. What is the probability that it is blue?",
                "options": ["1/3", "7/21", "1/2", "9/21"],
                "correct_index": 0,
                "explanation": "Total balls = 8 + 7 + 6 = 21. Blue balls = 7. Probability = 7/21 = 1/3."
            },
            {
                "question": "Three unbiased coins are tossed. What is the probability of getting at least 2 heads?",
                "options": ["1/4", "3/8", "1/2", "5/8"],
                "correct_index": 2,
                "explanation": "Sample space size = 8. Favorable outcomes (at least 2 heads): HHH, HHT, HTH, THH (4 outcomes). Probability = 4/8 = 1/2."
            },
            {
                "question": "Two cards are drawn together from a pack of 52 cards. What is the probability that one is a spade and one is a heart?",
                "options": ["13/102", "26/102", "13/51", "26/51"],
                "correct_index": 0,
                "explanation": "Probability = (13C1 * 13C1) / 52C2 = (13 * 13) / (26 * 51) = 13 / 102."
            }
        ],
        "Permutation & Combination": [
            {
                "question": "In how many ways can the letters of the word 'LEADER' be arranged?",
                "options": ["720", "360", "120", "1440"],
                "correct_index": 1,
                "explanation": "Word has 6 letters: E appears twice. Total arrangements = 6! / 2! = 720 / 2 = 360."
            },
            {
                "question": "In a group of 7 boys and 6 girls, 5 persons are to be selected to form a committee so that at least 3 boys are on the committee. In how many ways can it be done?",
                "options": ["564", "645", "735", "756"],
                "correct_index": 3,
                "explanation": "Cases: (3B, 2G) or (4B, 1G) or (5B). Ways = (7C3 * 6C2) + (7C4 * 6C1) + (7C5 * 6C0) = (35 * 15) + (35 * 6) + 21 = 525 + 210 + 21 = 756."
            },
            {
                "question": "Out of 7 consonants and 4 vowels, how many words of 3 consonants and 2 vowels can be formed?",
                "options": ["210", "25200", "24400", "21300"],
                "correct_index": 1,
                "explanation": "Selection ways = 7C3 * 4C2 = 35 * 6 = 210. Arrangement of 5 selected letters = 5! = 120. Total words = 210 * 120 = 25200."
            }
        ],
        "Profit & Loss": [
            {
                "question": "A shopkeeper sells an article for Rs. 300, making a profit of 25%. What is the cost price of the article?",
                "options": ["Rs. 220", "Rs. 240", "Rs. 250", "Rs. 260"],
                "correct_index": 1,
                "explanation": "CP * 1.25 = 300 => CP = 300 / 1.25 = 240."
            },
            {
                "question": "If a man sells his chair for Rs. 720, he would lose 25%. To gain 25%, he should sell it for:",
                "options": ["Rs. 960", "Rs. 1000", "Rs. 1200", "Rs. 1080"],
                "correct_index": 2,
                "explanation": "75% of CP = 720 => CP = 960. 125% of CP = 960 * 1.25 = 1200."
            },
            {
                "question": "A dishonest dealer claims to sell his goods at cost price but uses a weight of 960g for a kg. Find his gain percentage.",
                "options": ["4%", "4.16%", "4.25%", "4.5%"],
                "correct_index": 1,
                "explanation": "Gain% = [Error / (True Value - Error)] * 100 = [40 / 960] * 100 = 4.16%."
            }
        ],
        "Percentage": [
            {
                "question": "If A's salary is 20% less than B's salary, then how much percent is B's salary more than A's?",
                "options": ["20%", "25%", "30%", "33.33%"],
                "correct_index": 1,
                "explanation": "Formula: [R / (100 - R)] * 100 = [20 / 80] * 100 = 25%."
            },
            {
                "question": "In an election between two candidates, one got 55% of the total valid votes. 20% of the votes were invalid. If the total number of votes was 7500, what was the number of valid votes that the other candidate got?",
                "options": ["2700", "2900", "3000", "3100"],
                "correct_index": 0,
                "explanation": "Total valid votes = 80% of 7500 = 6000. Other candidate got 45% of valid votes = 0.45 * 6000 = 2700."
            },
            {
                "question": "What is 30% of 80% of 500?",
                "options": ["120", "150", "180", "100"],
                "correct_index": 0,
                "explanation": "80% of 500 = 400. 30% of 400 = 120."
            }
        ],
        "Ratio": [
            {
                "question": "If A:B = 2:3, B:C = 4:5 and C:D = 6:7, then A:D is:",
                "options": ["16:35", "12:35", "8:35", "24:35"],
                "correct_index": 0,
                "explanation": "A/D = (A/B) * (B/C) * (C/D) = (2/3) * (4/5) * (6/7) = 16/35."
            },
            {
                "question": "Two numbers are in the ratio 3:5. If 9 is subtracted from each, the new numbers are in the ratio 12:23. The smaller number is:",
                "options": ["27", "33", "49", "55"],
                "correct_index": 1,
                "explanation": "Let numbers be 3x and 5x. (3x-9)/(5x-9) = 12/23 => 69x - 207 = 60x - 108 => 9x = 99 => x = 11. Smaller number is 33."
            },
            {
                "question": "A sum of money is divided among A, B, C, D in the ratio 5:2:4:3. If C gets Rs. 1000 more than D, what is B's share?",
                "options": ["Rs. 500", "Rs. 1500", "Rs. 2000", "Rs. 1000"],
                "correct_index": 2,
                "explanation": "Difference in C and D parts = 4 - 3 = 1 part. 1 part = 1000. B's share is 2 parts = Rs. 2000."
            }
        ],
        "Simplification": [
            {
                "question": "Find the value of (0.337 + 0.126)^2 - (0.337 - 0.126)^2 / (0.337 * 0.126).",
                "options": ["1", "2", "4", "0.5"],
                "correct_index": 2,
                "explanation": "This is in the form of (a+b)^2 - (a-b)^2 / ab. (a+b)^2 - (a-b)^2 = 4ab. Thus, 4ab / ab = 4."
            },
            {
                "question": "Solve: 108 ÷ 9 + 2/5 * 13/4 = ?",
                "options": ["13 3/10", "8 2/5", "16/5", "10"],
                "correct_index": 0,
                "explanation": "108 ÷ 9 = 12. 2/5 * 13/4 = 13/10. 12 + 13/10 = 133/10 = 13 3/10."
            },
            {
                "question": "What is the square root of 0.0009?",
                "options": ["0.3", "0.03", "0.003", "0.9"],
                "correct_index": 1,
                "explanation": "0.03 * 0.03 = 0.0009. So, square root is 0.03."
            }
        ]
    },
    "logical": {
        "Blood Relation": [
            {
                "question": "Pointing to a photograph, a man said, 'I have no brother or sister but that man's father is my father's son.' Whose photograph was it?",
                "options": ["His nephew's", "His son's", "His father's", "His own"],
                "correct_index": 1,
                "explanation": "Since he has no brother or sister, his father's son is himself. So, the man in the photo's father is himself. Thus, it's his son's photograph."
            },
            {
                "question": "If A is B's sister, C is B's mother, D is C's father, and E is D's mother, how is A related to D?",
                "options": ["Grandmother", "Grandfather", "Daughter", "Granddaughter"],
                "correct_index": 3,
                "explanation": "A is sister of B, mother is C. So A is daughter of C. D is C's father. Thus, A is granddaughter of D."
            },
            {
                "question": "Introducing a woman, a man said, 'She is the only daughter of my mother's mother.' How is the woman related to the man?",
                "options": ["Mother", "Aunt", "Sister", "Niece"],
                "correct_index": 0,
                "explanation": "Mother's mother is grandmother. Her only daughter is the man's mother."
            }
        ],
        "Seating Arrangement": [
            {
                "question": "A, B, C, D, E, F and G are sitting in a row facing North. F is to the immediate right of E. E is 4th to the right of G. C is the neighbor of B and D. Person who is third to the left of D is at one of the ends. Who are sitting at the extreme ends?",
                "options": ["G and A", "G and F", "E and F", "C and D"],
                "correct_index": 0,
                "explanation": "Row arrangement is: G, B, C, D, E, F, A. G and A are at the ends."
            },
            {
                "question": "Six friends A, B, C, D, E and F are sitting in a circle facing the center. C is between A and E, D is between F and B. F is to the immediate left of A. Who is facing C?",
                "options": ["A", "B", "D", "E"],
                "correct_index": 2,
                "explanation": "Arrangement in circle is A, C, E, B, D, F. D is facing C."
            },
            {
                "question": "Five girls are sitting on a bench to be photographed. Seema is to the left of Rani and to the right of Bindu. Mary is to the right of Rani. Reeta is between Rani and Mary. Who is in the middle?",
                "options": ["Seema", "Rani", "Bindu", "Reeta"],
                "correct_index": 1,
                "explanation": "Bench order from left to right: Bindu, Seema, Rani, Reeta, Mary. Rani is in the middle."
            }
        ],
        "Coding Decoding": [
            {
                "question": "If in a certain language, MADRAS is coded as NBESBT, how is BOMBAY coded in that code?",
                "options": ["CPNCBX", "CPNCBZ", "CPOCBZ", "CQOCBZ"],
                "correct_index": 1,
                "explanation": "Each letter is shifted by +1. BOMBAY becomes CPNCBZ."
            },
            {
                "question": "In a certain code, '786' means 'study very hard', '958' means 'hard work pays' and '645' means 'study and work'. Find the code for 'very'.",
                "options": ["6", "7", "8", "5"],
                "correct_index": 1,
                "explanation": "'study very hard' = 786. 'hard work pays' = 958 => common is 'hard' = 8. 'study and work' = 645 => common with 1st is 'study' = 6. So 'very' = 7."
            },
            {
                "question": "If 'orange' is called 'butter', 'butter' is called 'soap', 'soap' is called 'ink', 'ink' is called 'honey' and 'honey' is called 'orange', which of the following is used for washing clothes?",
                "options": ["butter", "soap", "ink", "honey"],
                "correct_index": 2,
                "explanation": "Soap is used for washing clothes. Since soap is called ink, ink is used."
            }
        ],
        "Puzzle": [
            {
                "question": "There are five books A, B, C, D and E. Book C lies above D, Book E is below A; D is above A; B is below E. Which book is at the bottom?",
                "options": ["A", "B", "C", "D"],
                "correct_index": 1,
                "explanation": "Order from top to bottom: C, D, A, E, B. Book B is at the bottom."
            },
            {
                "question": "A, B, C, D and E are five boys. A is shorter than B but taller than E. C is the tallest. D is a little shorter than B and a little taller than A. Who is the shortest?",
                "options": ["A", "B", "D", "E"],
                "correct_index": 3,
                "explanation": "Height order: C > B > D > A > E. E is the shortest."
            },
            {
                "question": "Four players A, B, C, and D are playing cards. A and B are partners. D faces North. If A faces West, which direction does B face?",
                "options": ["North", "South", "East", "West"],
                "correct_index": 2,
                "explanation": "A faces West, so his partner B must face East."
            }
        ],
        "Syllogism": [
            {
                "question": "Statements: All bags are pockets. All pockets are pouches. Conclusions: I. All bags are pouches. II. Some pouches are bags.",
                "options": ["Only conclusion I follows", "Only conclusion II follows", "Either I or II follows", "Both I and II follow"],
                "correct_index": 3,
                "explanation": "Since pouches contain pockets which contain bags, all bags are pouches. And since bags are inside pouches, some pouches are bags."
            },
            {
                "question": "Statements: Some actors are singers. All singers are dancers. Conclusions: I. Some actors are dancers. II. No singer is actor.",
                "options": ["Only conclusion I follows", "Only conclusion II follows", "Neither I nor II follows", "Both I and II follow"],
                "correct_index": 0,
                "explanation": "Since some actors are singers, and all singers are dancers, those actors who are singers are also dancers. So I follows. II does not follow."
            },
            {
                "question": "Statements: All ants are bees. No bee is wasp. Conclusions: I. No ant is wasp. II. Some bees are ants.",
                "options": ["Only conclusion I follows", "Only conclusion II follows", "Both I and II follow", "Neither I nor II follows"],
                "correct_index": 2,
                "explanation": "Since all ants are bees, and bees have no intersection with wasps, ants also have no intersection with wasps (I follows). Since all ants are bees, some bees are ants (II follows)."
            }
        ],
        "Direction Sense": [
            {
                "question": "A man walks 5 km toward South and then turns to the right. After walking 3 km he turns to the left and walks 5 km. Now in which direction is he from the starting place?",
                "options": ["West", "South", "South-West", "North-East"],
                "correct_index": 2,
                "explanation": "He goes South, then West, then South. Overall he is in South-West direction."
            },
            {
                "question": "One morning after sunrise, Suresh was standing facing a pole. The shadow of the pole fell exactly to his right. To which direction was he facing?",
                "options": ["East", "West", "North", "South"],
                "correct_index": 3,
                "explanation": "Sun is in East, shadow is in West. Suresh's right side is West, so he must be facing South."
            },
            {
                "question": "A child is looking for his father. He went 90 m in the East before turning to his right. He went 20 m before turning to his right again to look for his father at his uncle's place 30 m from this point. From here he went 100 m to the North. How far did the son meet his father from the starting point?",
                "options": ["80 m", "100 m", "140 m", "260 m"],
                "correct_index": 1,
                "explanation": "Horizontal net distance = 90 - 30 = 60 m. Vertical net distance = 100 - 20 = 80 m. Straight line distance = sqrt(60^2 + 80^2) = 100 m."
            }
        ],
        "Statement & Assumption": [
            {
                "question": "Statement: 'Please do not lean out of the running train' - a warning in a train compartment. Assumptions: I. People generally ignore warnings. II. Leaning out of a running train is dangerous.",
                "options": ["Only I is implicit", "Only II is implicit", "Either I or II is implicit", "Neither I nor II is implicit"],
                "correct_index": 1,
                "explanation": "Warnings are posted because the action is dangerous (II is implicit). The warning assumes people will read and follow it, not ignore it (I is not implicit)."
            },
            {
                "question": "Statement: 'Apply heat therapy for joint pains' - Advice by a doctor. Assumptions: I. Heat therapy can relieve joint pain. II. Joint pains are common.",
                "options": ["Only I is implicit", "Only II is implicit", "Both I and II are implicit", "Neither I nor II is implicit"],
                "correct_index": 0,
                "explanation": "The doctor advises it because it works (I is implicit). The statement does not imply whether joint pain is common overall (II is not implicit)."
            },
            {
                "question": "Statement: 'Join our institute for guaranteed success' - An advertisement. Assumptions: I. Students want success. II. The institute provides good training.",
                "options": ["Only I is implicit", "Only II is implicit", "Both I and II are implicit", "Neither I nor II is implicit"],
                "correct_index": 2,
                "explanation": "Both assumptions are implicit: students want success (otherwise advertising it is useless), and the institute claims/assumes it provides good training to enable success."
            }
        ]
    },
    "verbal": {
        "Synonyms": [
            {
                "question": "Find the synonym of 'ABANDON'.",
                "options": ["Forsake", "Keep", "Cherish", "Adopt"],
                "correct_index": 0,
                "explanation": "Abandon means to leave or give up completely, which is synonymous with Forsake."
            },
            {
                "question": "Find the synonym of 'BRIEF'.",
                "options": ["Limited", "Small", "Short", "Little"],
                "correct_index": 2,
                "explanation": "Brief means concise or of short duration. Short is the closest synonym."
            },
            {
                "question": "Find the synonym of 'ALERT'.",
                "options": ["Energetic", "Observant", "Intelligent", "Watchful"],
                "correct_index": 3,
                "explanation": "Alert means quick to notice any unusual situation. Watchful is the correct synonym."
            }
        ],
        "Antonyms": [
            {
                "question": "Find the antonym of 'HARSH'.",
                "options": ["Gentle", "Rough", "Severe", "Bitter"],
                "correct_index": 0,
                "explanation": "Harsh means severe or rough. Gentle is the antonym."
            },
            {
                "question": "Find the antonym of 'ENORMOUS'.",
                "options": ["Soft", "Tiny", "Weak", "Fragile"],
                "correct_index": 1,
                "explanation": "Enormous means very large. Tiny is the antonym."
            },
            {
                "question": "Find the antonym of 'ARTIFICIAL'.",
                "options": ["Redundant", "Natural", "Truthful", "Solid"],
                "correct_index": 1,
                "explanation": "Artificial means man-made. Natural is the antonym."
            }
        ],
        "Reading Comprehension": [
            {
                "question": "Read: 'The industrial revolution marked a major turning point in history, influencing almost every aspect of daily life. Average income and population began to exhibit unprecedented growth.' What was the effect of the industrial revolution according to the text?",
                "options": ["Income and population grew rapidly", "Daily life became very difficult", "People stopped farming", "Industrial pollution increased"],
                "correct_index": 0,
                "explanation": "The text states 'Average income and population began to exhibit unprecedented growth'."
            },
            {
                "question": "Read: 'Despite their small brain size, ants exhibit complex social behaviors like division of labor, communication, and problem-solving.' What is the author's main point about ants?",
                "options": ["Ants have very large brains", "Ants are dangerous pests", "Ants show complex social behavior", "Ants cannot communicate"],
                "correct_index": 2,
                "explanation": "The text highlights that ants exhibit complex social behaviors."
            },
            {
                "question": "Read: 'Renewable energy sources such as solar and wind power are critical to reducing greenhouse gas emissions and combating climate change.' What is the primary benefit of solar and wind power mentioned?",
                "options": ["They are cheaper than coal", "They reduce greenhouse gas emissions", "They are easy to install", "They produce unlimited electricity"],
                "correct_index": 1,
                "explanation": "The text directly states they are critical to reducing greenhouse gas emissions."
            }
        ],
        "Grammar": [
            {
                "question": "Identify the correct sentence:",
                "options": ["Every student must bring their own book.", "Neither of the boys were present.", "He is one of those men who knows everything.", "She has been working since three hours."],
                "correct_index": 0,
                "explanation": "'Every student must bring their own book' is modern standard usage. 'Neither of the boys was present' is correct. 'She has been working for three hours' is correct."
            },
            {
                "question": "Fill in the blank: 'If I _____ a king, I would help the poor.'",
                "options": ["was", "were", "am", "would be"],
                "correct_index": 1,
                "explanation": "In subjunctive mood for imaginary situations, 'were' is used with all subjects."
            },
            {
                "question": "Choose the correct preposition: 'She was congratulated _____ her success.'",
                "options": ["for", "on", "about", "at"],
                "correct_index": 1,
                "explanation": "The standard idiom is 'congratulate someone on something'."
            }
        ],
        "Error Spotting": [
            {
                "question": "Find the part with the error: '(A) He is / (B) senior than me / (C) in service. / (D) No error'",
                "options": ["A", "B", "C", "D"],
                "correct_index": 1,
                "explanation": "Adjectives ending in 'ior' like senior, junior, prior are followed by 'to' instead of 'than'. It should be 'senior to me'."
            },
            {
                "question": "Find the part with the error: '(A) Unless you do not work / (B) hard, you / (C) cannot pass. / (D) No error'",
                "options": ["A", "B", "C", "D"],
                "correct_index": 0,
                "explanation": "'Unless' itself has a negative meaning. Using 'do not' with unless is a double negative. It should be 'Unless you work'."
            },
            {
                "question": "Find the part with the error: '(A) Many a student / (B) have failed / (C) in the test. / (D) No error'",
                "options": ["A", "B", "C", "D"],
                "correct_index": 1,
                "explanation": "'Many a' is followed by a singular noun and singular verb. It should be 'has failed'."
            }
        ],
        "Sentence Correction": [
            {
                "question": "Correct the underlined part: 'He told me that he <u>is writing</u> a letter.'",
                "options": ["is writing", "was writing", "has written", "had been writing"],
                "correct_index": 1,
                "explanation": "Due to sequence of tenses, since the reporting verb 'told' is in past, 'is writing' must change to 'was writing'."
            },
            {
                "question": "Correct the underlined part: 'Hardly had he arrived <u>then</u> it started raining.'",
                "options": ["then", "than", "when", "that"],
                "correct_index": 2,
                "explanation": "'Hardly' is paired with 'when' in a sentence structure (Hardly... when)."
            },
            {
                "question": "Correct the underlined part: 'He is <u>too weak to walk</u>.'",
                "options": ["too weak to walk", "too weak for walking", "so weak that cannot walk", "very weak to walk"],
                "correct_index": 0,
                "explanation": "The sentence 'too weak to walk' is grammatically correct and means he is so weak that he cannot walk."
            }
        ]
    },
    "technical": {
        "Java": [
            {
                "question": "Which of the following is NOT a feature of Java?",
                "options": ["Object-Oriented", "Use of pointers", "Platform Independent", "Multi-threaded"],
                "correct_index": 1,
                "explanation": "Java does not support explicit pointers to ensure memory safety."
            },
            {
                "question": "What is the size of 'char' variable in Java?",
                "options": ["8 bit", "16 bit", "32 bit", "Depends on platform"],
                "correct_index": 1,
                "explanation": "In Java, characters are represented using Unicode, occupying 16 bits (2 bytes)."
            },
            {
                "question": "Which class is the superclass of all classes in Java?",
                "options": ["String", "Object", "Class", "System"],
                "correct_index": 1,
                "explanation": "The Object class in the java.lang package is the root of the Java class hierarchy."
            }
        ],
        "Python": [
            {
                "question": "Which of the following is mutable in Python?",
                "options": ["List", "Tuple", "String", "Integer"],
                "correct_index": 0,
                "explanation": "Lists are mutable, meaning their elements can be modified. Tuples, strings, and integers are immutable."
            },
            {
                "question": "What is the output of 'print(type(1 / 2))' in Python 3?",
                "options": ["<class 'int'>", "<class 'float'>", "<class 'double'>", "Error"],
                "correct_index": 1,
                "explanation": "In Python 3, single division `/` always returns a float value, so 1/2 is 0.5."
            },
            {
                "question": "How do you start a comment in Python?",
                "options": ["//", "/*", "#", "<!--"],
                "correct_index": 2,
                "explanation": "Python uses the hash '#' symbol for single-line comments."
            }
        ],
        "C++": [
            {
                "question": "Which of the following is used to allocate memory dynamically in C++?",
                "options": ["malloc()", "new", "alloc()", "create"],
                "correct_index": 1,
                "explanation": "In C++, the 'new' operator is used for dynamic memory allocation."
            },
            {
                "question": "What is a virtual function in C++?",
                "options": ["A function that has no body", "A function defined in a base class and overridden by a derived class", "A function that cannot be inherited", "A function inside a struct"],
                "correct_index": 1,
                "explanation": "Virtual functions allow runtime polymorphism, letting derived classes override base class behavior."
            },
            {
                "question": "Which header file is used for standard input-output stream in C++?",
                "options": ["stdio.h", "conio.h", "iostream", "stdlib.h"],
                "correct_index": 2,
                "explanation": "C++ uses the <iostream> header file for console input-output operations."
            }
        ],
        "DBMS": [
            {
                "question": "Which of the following represents the ACID properties of a transaction?",
                "options": ["Atomicity, Consistency, Isolation, Durability", "Access, Control, Integration, Delivery", "Authentication, Cryptography, Integrity, Decryption", "Automation, Concurrency, Indexing, Data"],
                "correct_index": 0,
                "explanation": "ACID stands for Atomicity, Consistency, Isolation, and Durability."
            },
            {
                "question": "What is a Foreign Key?",
                "options": ["A key that uniquely identifies a record in the same table", "A key used to reference the Primary Key of another table", "A key that accepts null values only", "A candidate key representing indexes"],
                "correct_index": 1,
                "explanation": "A Foreign Key is a field in one table that uniquely identifies a row of another table (referential integrity)."
            },
            {
                "question": "In which normal form is a relation if it has no multi-valued dependencies?",
                "options": ["1NF", "2NF", "3NF", "4NF"],
                "correct_index": 3,
                "explanation": "A relation is in Fourth Normal Form (4NF) if it is in BCNF and contains no multi-valued dependencies."
            }
        ],
        "OOPS": [
            {
                "question": "Which OOP concept is described as wrapping data and code into a single unit?",
                "options": ["Inheritance", "Polymorphism", "Encapsulation", "Abstraction"],
                "correct_index": 2,
                "explanation": "Encapsulation restricts direct access to some of an object's components, wrapping data and methods together."
            },
            {
                "question": "What is method overloading?",
                "options": ["Writing a method with the same name but different signatures in the same class", "Writing a method with the same name and signature in a subclass", "Writing a method that takes multiple parameters", "Calling a method recursively"],
                "correct_index": 0,
                "explanation": "Method overloading is a compile-time polymorphism feature where multiple methods share the same name but differ in parameters."
            },
            {
                "question": "Which of the following is an abstract representation of an entity?",
                "options": ["Object", "Class", "Method", "Variable"],
                "correct_index": 1,
                "explanation": "A Class is a blueprint or template representing abstract features and behaviors of an entity."
            }
        ],
        "Operating System": [
            {
                "question": "What is a deadlock in an Operating System?",
                "options": ["A system crash", "A state where a set of processes are blocked because each holds a resource and waits for another", "A infinite loop in CPU scheduling", "A hardware failure"],
                "correct_index": 1,
                "explanation": "Deadlock occurs when processes are unable to proceed because they wait for resources held by each other."
            },
            {
                "question": "Which scheduling algorithm is non-preemptive?",
                "options": ["Round Robin", "Shortest Job First (SJF)", "Priority Scheduling", "First-Come, First-Served (FCFS)"],
                "correct_index": 3,
                "explanation": "FCFS always executes processes in the order of their arrival without preemption."
            },
            {
                "question": "What is virtual memory?",
                "options": ["A physical RAM upgrade", "An extension of physical memory using disk space to allow execution of larger programs", "A cache memory location", "Memory stored in cloud servers"],
                "correct_index": 1,
                "explanation": "Virtual memory simulates additional RAM by moving inactive pages of data to disk storage."
            }
        ],
        "Computer Networks": [
            {
                "question": "Which layer of the OSI model is responsible for routing packets?",
                "options": ["Physical Layer", "Data Link Layer", "Network Layer", "Transport Layer"],
                "correct_index": 2,
                "explanation": "The Network Layer is responsible for packet routing, logical addressing, and path determination."
            },
            {
                "question": "What does HTTP stand for?",
                "options": ["Hyper Text Transfer Protocol", "High Transfer Tech Protocol", "Hyper Transfer Terminal Protocol", "Home Text Transmission Protocol"],
                "correct_index": 0,
                "explanation": "HTTP stands for Hyper Text Transfer Protocol."
            },
            {
                "question": "What is the port number for HTTPS by default?",
                "options": ["80", "8080", "443", "22"],
                "correct_index": 2,
                "explanation": "HTTPS runs on port 443 by default, whereas HTTP runs on port 80."
            }
        ],
        "SQL": [
            {
                "question": "Which SQL statement is used to remove all records from a table without logging individual row deletions?",
                "options": ["DELETE", "DROP", "TRUNCATE", "REMOVE"],
                "correct_index": 2,
                "explanation": "TRUNCATE removes all rows from a table quickly without logging row deletions, whereas DELETE logs each row."
            },
            {
                "question": "What is the purpose of the GROUP BY clause?",
                "options": ["To filter rows based on conditions", "To sort the query results", "To group rows that have the same values into summary rows", "To join multiple tables"],
                "correct_index": 2,
                "explanation": "GROUP BY is used with aggregate functions (COUNT, MAX, MIN, SUM, AVG) to group results by one or more columns."
            },
            {
                "question": "Which join returns all rows from the left table and matched rows from the right table?",
                "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"],
                "correct_index": 1,
                "explanation": "A LEFT JOIN returns all records from the left table, and the matched records from the right table (returning NULL if no match)."
            }
        ],
        "HTML": [
            {
                "question": "What does HTML stand for?",
                "options": ["Hyper Text Markup Language", "Home Tool Markup Language", "Hyperlink Text Management Language", "Hyper Tech Media Language"],
                "correct_index": 0,
                "explanation": "HTML stands for Hyper Text Markup Language."
            },
            {
                "question": "Which HTML tag is used to create a hyperlink?",
                "options": ["<link>", "<a>", "<href>", "<url>"],
                "correct_index": 1,
                "explanation": "The anchor tag <a> is used to define hyperlinks."
            },
            {
                "question": "Which attribute is used to specify an image source URL?",
                "options": ["href", "src", "alt", "link"],
                "correct_index": 1,
                "explanation": "The 'src' attribute specifies the path/URL to the image in an <img> tag."
            }
        ],
        "CSS": [
            {
                "question": "What is the default value of the position property in CSS?",
                "options": ["relative", "absolute", "static", "fixed"],
                "correct_index": 2,
                "explanation": "The default positioning for HTML elements is static (positioned according to the normal flow of the page)."
            },
            {
                "question": "How do you select an element with ID 'header' in CSS?",
                "options": [".header", "#header", "header", "*header"],
                "correct_index": 1,
                "explanation": "CSS uses the hash '#' symbol for ID selectors, and dot '.' for class selectors."
            },
            {
                "question": "Which property is used to change the background color of an element?",
                "options": ["color", "bg-color", "background-color", "element-color"],
                "correct_index": 2,
                "explanation": "The 'background-color' property sets the background color of an element."
            }
        ],
        "JavaScript": [
            {
                "question": "What is the output of 'console.log(typeof null)'?",
                "options": ["'null'", "'undefined'", "'object'", "'string'"],
                "correct_index": 2,
                "explanation": "This is a long-standing bug in JavaScript where null evaluates to 'object' due to how values were represented."
            },
            {
                "question": "Which keyword is used to declare a block-scoped variable that cannot be reassigned?",
                "options": ["var", "let", "const", "readonly"],
                "correct_index": 2,
                "explanation": "'const' declares a block-scoped constant value that cannot be reassigned."
            },
            {
                "question": "Which method joins all elements of an array into a string?",
                "options": ["join()", "concat()", "combine()", "toString()"],
                "correct_index": 0,
                "explanation": "The array.join() method joins all elements of an array into a single string separated by a specified separator."
            }
        ],
        "React": [
            {
                "question": "What is the purpose of React keys?",
                "options": ["To encrypt components", "To identify which items have changed, been added, or removed in a list", "To bind click handlers", "To manage global state"],
                "correct_index": 1,
                "explanation": "Keys help React identify which items in a list are changed/updated, ensuring efficient virtual DOM reconciliation."
            },
            {
                "question": "Which hook is used to perform side effects in a functional component?",
                "options": ["useState", "useContext", "useEffect", "useReducer"],
                "correct_index": 2,
                "explanation": "The useEffect hook lets you perform side effects (data fetching, subscriptions, DOM updates) in function components."
            },
            {
                "question": "What is JSX?",
                "options": ["A JavaScript framework", "A syntax extension for JavaScript that looks like HTML", "A template engine for Node.js", "A package manager for React"],
                "correct_index": 1,
                "explanation": "JSX stands for JavaScript XML. It is a syntax extension for JavaScript used with React to describe UI appearance."
            }
        ],
        "AI/ML": [
            {
                "question": "What is the main difference between Supervised and Unsupervised learning?",
                "options": ["Supervised uses labeled data; Unsupervised uses unlabeled data", "Supervised is for classification only; Unsupervised is for regression", "Supervised does not use loss functions", "Unsupervised does not require training"],
                "correct_index": 0,
                "explanation": "Supervised learning relies on training data that contains both inputs and their matching ground truth labels."
            },
            {
                "question": "Which activation function is commonly used in the output layer of a binary classification neural network?",
                "options": ["ReLU", "Tanh", "Sigmoid", "Softmax"],
                "correct_index": 2,
                "explanation": "The Sigmoid function squashes outputs between 0 and 1, making it ideal for representing binary probability."
            },
            {
                "question": "What is Overfitting in Machine Learning?",
                "options": ["A model that performs poorly on both training and test data", "A model that performs well on training data but poorly on unseen test data", "A model that takes too long to train", "A model with too few parameters"],
                "correct_index": 1,
                "explanation": "Overfitting happens when a model learns noise and details in training data so much that it hurts generalization to new data."
            }
        ]
    }
}
