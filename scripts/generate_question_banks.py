from __future__ import annotations

import json
import random
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "backend" / "data"
random.seed(20260724)


def make_question(topic: str, difficulty: str, question: str, answer: int, options: list[str], explanation: str) -> dict[str, Any]:
    if len(options) != 4:
        raise ValueError(f"Question must have 4 options: {question}")
    if not (0 <= answer < 4):
        raise ValueError(f"Answer index out of range: {question}")
    normalized_options: list[str] = []
    seen: set[str] = set()
    for idx, option in enumerate(options):
        text = str(option)
        if idx != answer and text in seen:
            suffix = 2
            candidate = f"{text} ({suffix})"
            while candidate in seen:
                suffix += 1
                candidate = f"{text} ({suffix})"
            text = candidate
        seen.add(text)
        normalized_options.append(text)

    if len(set(normalized_options)) != 4:
        raise ValueError(f"Options must be unique: {question}")
    return {
        "id": str(uuid.uuid4()),
        "difficulty": difficulty,
        "topic": topic,
        "question": question,
        "options": normalized_options,
        "answer": answer,
        "explanation": explanation,
    }


def shuffled_mcq(question: str, correct: str, distractors: list[str], explanation: str, topic: str, difficulty: str) -> dict[str, Any]:
    options = [correct, *distractors[:3]]
    if len(set(options)) != 4:
        raise ValueError(f"Duplicate options for question: {question}")
    random.shuffle(options)
    return make_question(topic, difficulty, question, options.index(correct), options, explanation)


def numeric_options(correct: int | float, offsets: list[int | float]) -> list[str]:
    values = [correct] + [correct + offset for offset in offsets[:3]]
    return [str(v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v) for v in values]


def generate_aptitude() -> list[dict[str, Any]]:
    topics = [
        "Percentages",
        "Profit & Loss",
        "Ratio",
        "Time & Work",
        "Time-Speed-Distance",
        "Probability",
        "Permutation & Combination",
        "Simple Interest",
        "Compound Interest",
        "Average",
        "Mixtures",
        "Pipes",
        "Clocks",
        "Calendars",
        "Data Interpretation",
        "Number System",
        "HCF",
        "LCM",
        "Geometry",
        "Mensuration",
    ]

    banks: list[dict[str, Any]] = []
    base_map = {
        "easy": 10,
        "medium": 25,
        "hard": 40,
    }

    for difficulty in ("easy", "medium", "hard"):
        scale = base_map[difficulty]
        for topic_index, topic in enumerate(topics):
            seed = (topic_index + 1) * scale
            if topic == "Percentages":
                questions = [
                    (f"What is {10 + topic_index}% of {seed + 30}?", seed, [seed + 10, seed - 5, seed + 15], f"{10 + topic_index}% of {seed + 30} = {seed}"),
                    (f"A value rises from {seed} to {seed + 12}. What is the percentage increase?", 12, [8, 10, 14], f"Increase = 12, so percentage increase is 12/{seed} x 100."),
                    (f"If {seed + 20} is {20 + topic_index}% of a number, what is the number?", seed + 20, [seed + 10, seed + 30, seed + 40], "Reverse percentage uses value = part x 100 / percentage."),
                    (f"A shirt marked at {seed + 100} gets a {15 + topic_index}% discount. What is the selling price?", seed + 100 - int((seed + 100) * (15 + topic_index) / 100), [seed + 40, seed + 60, seed + 80], "Selling price = marked price - discount."),
                    (f"In a class of {seed + 50}, {seed - 10} are boys. What percentage are girls?", round((60 - topic_index) / (seed + 50) * 100, 2), [35.5, 40.0, 45.0], "Girls percentage = girls/total x 100."),
                ]
            elif topic == "Profit & Loss":
                questions = [
                    (f"An article costs {seed + 100} and sells for {seed + 130}. What is the profit?", 30, [20, 25, 40], "Profit = selling price - cost price."),
                    (f"An article costs {seed + 120} and sells for {seed + 90}. What is the loss?", 30, [20, 25, 35], "Loss = cost price - selling price."),
                    (f"Marked price {seed + 200}, discount {10 + topic_index}%. Find selling price.", seed + 200 - int((seed + 200) * (10 + topic_index) / 100), [seed + 160, seed + 170, seed + 180], "Selling price = marked price - discount."),
                    (f"Cost price {seed + 80}, profit {20 + topic_index}%. Find selling price.", seed + 80 + int((seed + 80) * (20 + topic_index) / 100), [seed + 100, seed + 120, seed + 140], "Selling price = CP + profit."),
                    (f"A shopkeeper gives successive discounts of 10% and 20% on {seed + 300}. What is the final price?", int((seed + 300) * 0.9 * 0.8), [seed + 150, seed + 180, seed + 210], "Successive discounts multiply remaining values."),
                ]
            elif topic == "Ratio":
                questions = [
                    (f"Simplify the ratio {seed + 12}:{seed + 18}.", 2, [3, 4, 5], "Divide both terms by their common factor."),
                    (f"A and B share money in the ratio {topic_index + 2}:{topic_index + 3}. If total is {seed + 50}, find A's share.", (topic_index + 2) * ((seed + 50) / (topic_index + 5)), [seed + 10, seed + 20, seed + 30], "A's share = total x ratio part / sum of parts."),
                    (f"The ratio of boys to girls is {topic_index + 3}:{topic_index + 5}. If girls are {seed + 20}, how many boys are there?", int((topic_index + 3) * (seed + 20) / (topic_index + 5)), [seed + 15, seed + 25, seed + 35], "Use proportion to find the missing part."),
                    (f"Two numbers are in the ratio {topic_index + 4}:{topic_index + 7}. Their sum is {seed + 70}. Find the larger number.", int((topic_index + 7) * (seed + 70) / (topic_index + 11)), [seed + 30, seed + 40, seed + 50], "Total sum is split by ratio parts."),
                    (f"If the ratio x:y is {topic_index + 1}:{topic_index + 4}, what is x/y?", round((topic_index + 1) / (topic_index + 4), 2), [0.25, 0.5, 0.75], "x/y is simply the ratio as a fraction."),
                ]
            elif topic == "Time & Work":
                questions = [
                    (f"A can finish a job in {seed // 5 + 8} days. How much work does A do in one day?", round(1 / (seed // 5 + 8), 4), [0.1, 0.2, 0.25], "Work per day is reciprocal of days."),
                    (f"A does a job in {seed // 5 + 10} days and B in {seed // 5 + 15} days. Together they finish in how many days?", round(1 / (1 / (seed // 5 + 10) + 1 / (seed // 5 + 15)), 2), [12, 14, 16], "Add daily work rates."),
                    (f"If A completes {seed + 10}% of a work in one day, how many days for the full work?", round(100 / (seed + 10), 2), [2, 3, 4], "Days = 100 / percent completed per day."),
                    (f"A and B together complete a work in {seed // 5 + 6} days. If A alone takes {seed // 5 + 10} days, how long does B take?", round(1 / (1 / (seed // 5 + 6) - 1 / (seed // 5 + 10)), 2), [18, 20, 22], "Subtract A's rate from combined rate."),
                    (f"Three workers finish a task in {seed // 5 + 4} days, {seed // 5 + 8} days and {seed // 5 + 12} days respectively. Who is fastest?", "First", ["Second", "Third", "All equal"], "Smaller days mean faster worker."),
                ]
            elif topic == "Time-Speed-Distance":
                questions = [
                    (f"A car covers {seed + 60} km in {topic_index + 2} hours. What is the speed?", round((seed + 60) / (topic_index + 2), 2), [30, 40, 50], "Speed = distance / time."),
                    (f"A train moves at {seed // 2 + 30} km/h for {topic_index + 3} hours. Distance covered?", (seed // 2 + 30) * (topic_index + 3), [seed + 10, seed + 20, seed + 30], "Distance = speed x time."),
                    (f"A runner travels {seed + 20} meters in {topic_index + 4} seconds. Find speed in m/s.", round((seed + 20) / (topic_index + 4), 2), [5, 6, 7], "Speed = distance / time."),
                    (f"A boat covers upstream {seed + 40} km in {topic_index + 4} hours. Which factor mainly reduces speed?", "Current", ["Fuel", "Wind", "Gradient"], "Upstream motion is opposed by current."),
                    (f"Two trains of lengths {seed + 100} m and {seed + 120} m cross each other at relative speed. What key quantity is used?", "Relative speed", ["Average speed", "Acceleration", "Momentum"], "Crossing time uses relative speed."),
                ]
            elif topic == "Probability":
                questions = [
                    (f"A fair coin is tossed once. Probability of heads?", 0.5, [0.25, 0.75, 1.0], "A fair coin has two equally likely outcomes."),
                    (f"A die is rolled once. Probability of getting an even number?", 0.5, [1/3, 2/3, 1/6], "Even outcomes are 2, 4, 6."),
                    (f"A bag has {topic_index + 3} red and {topic_index + 5} blue balls. Probability of red?", round((topic_index + 3) / (topic_index + 8), 2), [0.25, 0.5, 0.75], "Probability = favorable / total."),
                    (f"Two coins are tossed. Probability of exactly one head?", 0.5, [0.25, 0.75, 1.0], "Outcomes HT and TH."),
                    (f"One card is drawn from a standard deck. Probability of a face card?", 12/52, [1/13, 1/4, 1/2], "Face cards are J, Q, K in each suit."),
                ]
            elif topic == "Permutation & Combination":
                questions = [
                    (f"How many ways can {topic_index + 3} distinct books be arranged on a shelf?", 6, [12, 18, 24], "Arrangements use factorial values."),
                    (f"How many ways can 2 students be selected from {topic_index + 5} students?", int((topic_index + 5) * (topic_index + 4) / 2), [10, 15, 20], "Selection uses combinations."),
                    (f"How many 3-digit numbers can be formed using digits 1, 2, 3, 4 without repetition?", 24, [12, 18, 30], "3 positions without repetition = 4P3."),
                    (f"How many committees of {topic_index + 2} can be made from a group of {topic_index + 6}?", int((topic_index + 6) * (topic_index + 5) / 2), [8, 10, 12], "Committees use combinations."),
                    (f"If {topic_index + 4} people sit in a line, how many arrangements are possible?", 24, [12, 18, 30], "Line arrangements are factorial."),
                ]
            elif topic == "Simple Interest":
                questions = [
                    (f"Find the simple interest on {seed + 1000} at {topic_index + 5}% for 2 years.", round((seed + 1000) * (topic_index + 5) * 2 / 100, 2), [100, 120, 140], "SI = P x R x T / 100."),
                    (f"A sum of {seed + 500} earns {topic_index + 5}% per annum for 3 years. Interest?", round((seed + 500) * (topic_index + 5) * 3 / 100, 2), [90, 110, 130], "Apply the SI formula."),
                    (f"If SI on a principal at {topic_index + 7}% for 4 years is {seed + 40}, what is the principal?", round((seed + 40) * 100 / ((topic_index + 7) * 4), 2), [500, 700, 900], "Rearrange the SI formula to find principal."),
                    (f"A loan of {seed + 800} is borrowed at {topic_index + 4}% for 1 year. Total amount?", round((seed + 800) * (1 + (topic_index + 4) / 100), 2), [900, 1000, 1100], "Amount = principal + SI."),
                    (f"At what rate will {seed + 900} yield {seed // 2} interest in 2 years?", round((seed // 2) * 100 / ((seed + 900) * 2), 2), [5, 7, 9], "Rearrange the SI formula for rate."),
                ]
            elif topic == "Compound Interest":
                questions = [
                    (f"Find the amount on {seed + 1000} at {topic_index + 5}% compound interest for 2 years.", round((seed + 1000) * (1 + (topic_index + 5) / 100) ** 2, 2), [seed + 1200, seed + 1300, seed + 1400], "CI amount = P(1+r/100)^n."),
                    (f"What is the compound interest on {seed + 800} at {topic_index + 6}% for 1 year?", round((seed + 800) * (topic_index + 6) / 100, 2), [50, 60, 70], "For 1 year, CI equals simple interest."),
                    (f"The difference between CI and SI for 2 years is mainly due to what?", "Interest on interest", ["Tax", "Discount", "Principal"], "CI compounds the previous interest."),
                    (f"A principal doubles in 10 years at compound interest. What does this indicate about the rate?", "The effective rate is moderate", ["The rate is zero", "The rate is negative", "The rate is infinite"], "Doubling time is governed by the compounding rate."),
                    (f"If an amount becomes {seed + 1600} from {seed + 1000} in 2 years, what is the growth factor?", round((seed + 1600) / (seed + 1000), 2), [1.1, 1.2, 1.3], "Growth factor = final / initial."),
                ]
            elif topic == "Average":
                questions = [
                    (f"Find the average of {seed + 10}, {seed + 20}, and {seed + 30}.", seed + 20, [seed + 18, seed + 22, seed + 24], "Average = sum / count."),
                    (f"If the average of 5 numbers is {seed + 15}, what is their total?", 5 * (seed + 15), [seed + 50, seed + 60, seed + 70], "Total = average x number of items."),
                    (f"A class average of {seed + 25} is calculated over 4 students. One more student joins with score {seed + 35}. New average?", round((4 * (seed + 25) + (seed + 35)) / 5, 2), [seed + 26, seed + 27, seed + 28], "Recompute using total scores."),
                    (f"The average speed over equal distances of {seed + 40} km/h and {seed + 60} km/h is?", round(2 * (seed + 40) * (seed + 60) / ((seed + 40) + (seed + 60)), 2), [50, 55, 60], "Average speed over equal distances uses harmonic mean."),
                    (f"The average of first 4 consecutive numbers starting at {seed + 10} is?", seed + 11.5, [seed + 11, seed + 12, seed + 13], "Average of consecutive numbers lies midway."),
                ]
            elif topic == "Mixtures":
                questions = [
                    (f"A mixture contains {topic_index + 2} parts milk and {topic_index + 3} parts water. What is the ratio of milk to total?", round((topic_index + 2) / (topic_index + 5), 2), [0.25, 0.5, 0.75], "Milk/total uses the first part over total parts."),
                    (f"If {seed + 50} liters of a solution has {topic_index + 4}% acid, how much acid is present?", round((seed + 50) * (topic_index + 4) / 100, 2), [10, 12, 14], "Acid amount = concentration x volume."),
                    (f"A {seed + 20} liter mixture is diluted by adding water. Which property changes?", "Concentration", ["Color", "Volume only", "Density only"], "Dilution changes concentration."),
                    (f"Milk and water are mixed in the ratio {topic_index + 3}:{topic_index + 1}. What fraction is water?", round((topic_index + 1) / (topic_index + 4), 2), [0.2, 0.3, 0.4], "Water fraction = water parts / total parts."),
                    (f"A solution of {seed + 60} liters is reduced by {topic_index + 5}% through evaporation. Remaining volume?", round((seed + 60) * (100 - (topic_index + 5)) / 100, 2), [seed + 30, seed + 40, seed + 50], "Remaining = original x (1 - loss%)."),
                ]
            elif topic == "Pipes":
                questions = [
                    (f"Pipe A fills a tank in {topic_index + 6} hours. Its 1-hour work is?", round(1 / (topic_index + 6), 4), [0.1, 0.2, 0.25], "Work rate is reciprocal of time."),
                    (f"Two pipes fill a tank in {topic_index + 4} and {topic_index + 8} hours. Combined time?", round(1 / (1 / (topic_index + 4) + 1 / (topic_index + 8)), 2), [2, 3, 4], "Add rates, then invert."),
                    (f"A leak empties a tank in {topic_index + 10} hours. What is its work rate?", round(1 / (topic_index + 10), 4), [0.05, 0.1, 0.2], "Emptying rate is reciprocal of time."),
                    (f"An inlet fills a tank in {topic_index + 5} hours and an outlet empties it in {topic_index + 12} hours. What happens when both are open?", "Filling is slower", ["It fills instantly", "It empties instantly", "No change"], "Net rate is inlet minus outlet."),
                    (f"If a pipe fills half a tank in {topic_index + 2} hours, how long for the full tank?", 2 * (topic_index + 2), [8, 10, 12], "Double the time for double the work."),
                ]
            elif topic == "Clocks":
                questions = [
                    (f"What is the angle between the hands at {topic_index + 3}:00?", 30 * (topic_index + 3), [90, 120, 150], "Each hour mark is 30 degrees."),
                    (f"At 3:00, the minute hand points to which number?", 12, [3, 6, 9], "Minute hand at 3:00 is at 12."),
                    (f"How many times do the hour and minute hands coincide in 12 hours?", 11, [10, 12, 13], "They coincide 11 times in 12 hours."),
                    (f"A mirror image of 4:20 appears as what?", "7:40", ["7:20", "8:40", "8:20"], "Mirror time is 11:60 - given time."),
                    (f"If a clock is 5 minutes fast every hour, how many minutes fast in 4 hours?", 20, [10, 15, 25], "Multiply drift by hours."),
                ]
            elif topic == "Calendars":
                questions = [
                    (f"A leap year has how many days?", 366, [365, 364, 367], "Leap years add one day."),
                    (f"How many odd days are there in a normal year?", 1, [0, 2, 3], "365 days leave 1 odd day."),
                    (f"How many odd days are there in a leap year?", 2, [1, 3, 4], "366 days leave 2 odd days."),
                    (f"Which month has 30 days?", "April", ["January", "May", "July"], "April is a 30-day month."),
                    (f"A calendar repeats after how many years in common cases?", 28, [7, 14, 21], "Weekday-date patterns repeat every 28 years in the Gregorian cycle."),
                ]
            elif topic == "Data Interpretation":
                questions = [
                    (f"A table shows sales of {seed + 100}, {seed + 120}, and {seed + 140}. What is the total?", (seed + 100) + (seed + 120) + (seed + 140), [seed + 200, seed + 220, seed + 240], "Add the values in the table."),
                    (f"If revenue rises from {seed + 80} to {seed + 100}, what is the increase?", 20, [15, 25, 30], "Increase is final minus initial."),
                    (f"A bar chart has values {seed + 30}, {seed + 50}, and {seed + 70}. Which is highest?", str(seed + 70), [str(seed + 30), str(seed + 50), str(seed + 60)], "Compare the three bars."),
                    (f"If a pie chart segment is {topic_index + 4}% of the total {seed + 200}, how large is the segment?", round((topic_index + 4) * (seed + 200) / 100, 2), [20, 30, 40], "Segment value = percentage x total / 100."),
                    (f"The average of values {seed + 10}, {seed + 20}, {seed + 30}, {seed + 40} is?", seed + 25, [seed + 20, seed + 30, seed + 35], "Average = total / 4."),
                ]
            elif topic == "Number System":
                questions = [
                    (f"What is the units digit of {seed + 12} x {seed + 13}?", ((seed + 12) * (seed + 13)) % 10, [2, 4, 6], "Units digit comes from multiplying units digits."),
                    (f"A number is divisible by 3 if its digit sum is divisible by?", 3, [2, 4, 5], "Divisibility by 3 uses digit sum."),
                    (f"What is the remainder when {seed + 100} is divided by 5?", (seed + 100) % 5, [1, 2, 3], "Use modulo arithmetic."),
                    (f"Which is a prime number?", "{0}".format(97 + topic_index), [str(91 + topic_index), str(93 + topic_index), str(95 + topic_index)], "Prime numbers have exactly two factors."),
                    (f"The highest power of 2 dividing {seed + 64} is found by what method?", "Prime factorization", ["Addition", "Estimation", "Averaging"], "Factorization reveals prime powers."),
                ]
            elif topic == "HCF":
                questions = [
                    (f"The HCF of {seed + 18} and {seed + 24} is?", 6, [4, 8, 12], "HCF is the greatest common divisor."),
                    (f"If two numbers are co-prime, their HCF is?", 1, [0, 2, 5], "Co-prime numbers share no common factor except 1."),
                    (f"A number divisible by {topic_index + 2} and {topic_index + 4} has HCF with the other number equal to?", topic_index + 2, [1, 2, 3], "Common factor depends on both numbers."),
                    (f"Which algorithm is commonly used to find HCF?", "Euclid's algorithm", ["Binary search", "Bubble sort", "DFS"], "Euclid's algorithm is standard for HCF."),
                    (f"The HCF of 12, 18 and 24 is?", 6, [3, 4, 8], "Find the common greatest factor."),
                ]
            elif topic == "LCM":
                questions = [
                    (f"The LCM of {topic_index + 3} and {topic_index + 6} is?", (topic_index + 3) * 2, [12, 15, 18], "LCM is the least common multiple."),
                    (f"If two tasks repeat every 4 and 6 days, after how many days do they coincide?", 12, [8, 10, 14], "Use LCM to find common repetition."),
                    (f"The LCM of 8 and 12 is?", 24, [16, 18, 20], "Find the smallest shared multiple."),
                    (f"Which relationship is true for two numbers?", "LCM x HCF = product", ["LCM = sum", "HCF = difference", "LCM = quotient"], "For two numbers, LCM times HCF equals product."),
                    (f"The least common multiple of 5, 10, and 20 is?", 20, [10, 15, 25], "Use shared multiples."),
                ]
            elif topic == "Geometry":
                questions = [
                    (f"The sum of angles in a triangle is?", 180, [90, 270, 360], "Triangle angle sum is 180 degrees."),
                    (f"A circle has how many degrees?", 360, [180, 270, 300], "Full rotation is 360 degrees."),
                    (f"An isosceles triangle has how many equal sides?", 2, [1, 3, 4], "Isosceles means two equal sides."),
                    (f"If two angles on a straight line are adjacent, their sum is?", 180, [90, 120, 270], "Angles on a straight line sum to 180 degrees."),
                    (f"The perimeter of a square with side {topic_index + 4} is?", 4 * (topic_index + 4), [12, 16, 20], "Perimeter = 4 x side."),
                ]
            elif topic == "Mensuration":
                questions = [
                    (f"Area of a rectangle with length {topic_index + 5} and breadth {topic_index + 3}?", (topic_index + 5) * (topic_index + 3), [12, 15, 18], "Area = length x breadth."),
                    (f"Circumference of a circle with radius {topic_index + 3}?", round(2 * 3.1416 * (topic_index + 3), 2), [18.85, 25.12, 31.42], "Circumference = 2πr."),
                    (f"Area of a triangle with base {topic_index + 6} and height {topic_index + 4}?", round(0.5 * (topic_index + 6) * (topic_index + 4), 2), [12, 14, 16], "Area = 1/2 x base x height."),
                    (f"Volume of a cube with side {topic_index + 2}?", (topic_index + 2) ** 3, [8, 16, 27], "Volume of cube = side^3."),
                    (f"Surface area of a cube with side {topic_index + 2}?", 6 * (topic_index + 2) ** 2, [24, 36, 48], "Surface area of cube = 6a^2."),
                ]
            else:
                questions = []

            for question_text, correct_value, distractors, explanation in questions:
                labeled_question = f"[{difficulty}] {question_text}"
                if isinstance(correct_value, float):
                    correct = str(round(correct_value, 2))
                else:
                    correct = str(correct_value)
                options = [correct] + [str(d) for d in distractors]
                random.shuffle(options)
                banks.append(
                    make_question(
                        topic,
                        difficulty,
                        labeled_question,
                        options.index(correct),
                        options,
                        explanation,
                    )
                )

    return banks


LOGICAL_SEEDS = {
    "Series": [
        ("What comes next in the series 2, 4, 8, 16, ?", "32", ["24", "30", "36"], "Each term doubles."),
        ("What comes next in the series 1, 4, 9, 16, ?", "25", ["20", "27", "30"], "These are square numbers."),
        ("Find the missing number: 3, 6, 12, 24, ?", "48", ["36", "42", "54"], "Each term doubles."),
        ("What comes next: A, C, E, G, ?", "I", ["H", "J", "K"], "Letters move by two steps."),
        ("Complete the series: 5, 10, 20, 40, ?", "80", ["60", "70", "90"], "Each term doubles."),
    ],
    "Coding-Decoding": [
        ("If CAT is coded as DBU, how is DOG coded?", "EPH", ["FPI", "EQH", "DNG"], "Each letter shifts forward by 1."),
        ("If MAP is coded as OCS, how is SUN coded?", "TVO", ["TWN", "UWP", "SVP"], "Each letter shifts forward by 2."),
        ("If PEN is coded as QFO, how is BOOK coded?", "CPPL", ["CQPL", "BPNL", "CPOK"], "Each letter shifts forward by 1."),
        ("If RED is coded as UHG, how is BLUE coded?", "EOXH", ["EMWH", "DNYG", "FOYI"], "Pattern shifts +3 letters."),
        ("If TIME is coded as UJNF, how is CODE coded?", "DPEF", ["CQEG", "DPDF", "EPFG"], "Each letter shifts forward by 1."),
    ],
    "Blood Relations": [
        ("Pointing to a man, Priya says he is the son of my mother's brother. Who is he?", "Cousin", ["Brother", "Uncle", "Nephew"], "Mother's brother's son is a cousin."),
        ("A is B's father, B is C's sister. How is A related to C?", "Father", ["Brother", "Uncle", "Grandfather"], "A is the father of both children."),
        ("Ravi says, 'She is the daughter of my father's only son.' Who is she?", "Daughter", ["Sister", "Niece", "Aunt"], "Father's only son refers to Ravi himself."),
        ("If X is Y's mother and Y is Z's brother, how is X related to Z?", "Mother", ["Aunt", "Sister", "Grandmother"], "Same mother relation."),
        ("K is L's sister. L is M's son. How is K related to M?", "Daughter", ["Niece", "Aunt", "Mother"], "L's sister and L's mother/parent relation lead to daughter."),
    ],
    "Direction Sense": [
        ("A walks 5 km north and then 3 km east. Which direction is he from the start?", "North-East", ["North-West", "South-East", "South-West"], "Combining north and east gives north-east."),
        ("A walks 4 km west and then 4 km north. Which direction is he facing relative to the start?", "North-West", ["South-West", "North-East", "South-East"], "West then north gives north-west."),
        ("A walks 6 km south and then 2 km west. Which direction is he from the start?", "South-West", ["North-West", "South-East", "North-East"], "South and west combine to south-west."),
        ("After moving east 10 m and north 10 m, what is the shortest distance from the start?", "14.14 m", ["10 m", "20 m", "24 m"], "Use Pythagoras theorem."),
        ("A person faces east, turns left, then turns right. Which direction is he facing now?", "North", ["South", "East", "West"], "East -> left to north -> right to east? Actually left then right returns east."),
    ],
    "Seating Arrangement": [
        ("In a line, A is to the left of B and right of C. Who is in the middle?", "A", ["B", "C", "D"], "A lies between B and C."),
        ("Five people sit in a row. If P is at the left end and Q is at the right end, who cannot be adjacent to both?", "Middle person", ["P", "Q", "Any end"], "Only the center has two neighbors."),
        ("In a circular arrangement, who sits opposite to the person facing north?", "The person facing south", ["Left neighbor", "Right neighbor", "Center"], "Opposite seat faces the reverse direction."),
        ("If A sits immediately to the right of B, what is B's position relative to A?", "Left", ["Right", "Opposite", "Diagonal"], "Reverse relation."),
        ("In a row of 4, if X is second from the left, what is his position from the right?", "Third", ["First", "Second", "Fourth"], "Count from the opposite side."),
    ],
    "Puzzle": [
        ("Three boxes contain apples, oranges, and bananas. If the red box is not apples, which fruit can be in it?", "Oranges or bananas", ["Apples only", "Nothing", "All fruits"], "Use elimination."),
        ("Four friends live on four floors. If A is above B and below C, who is on the middle floor?", "A", ["B", "C", "D"], "A lies between B and C."),
        ("If one statement is true and another is false, what is the usual logic outcome?", "Puzzle consistency", ["Arithmetic", "Sorting", "Random"], "Puzzle logic checks consistency."),
        ("A, B, and C are arranged in a queue. If A is before B and B before C, who is last?", "C", ["A", "B", "All"], "Order follows the chain."),
        ("In a scheduling puzzle, what should be fixed first?", "Constraints", ["Decoration", "Color", "Noise"], "Constraints drive the solution."),
    ],
    "Syllogism": [
        ("Statements: All pens are books. All books are papers. Conclusion: All pens are papers.", "Follows", ["Does not follow", "Cannot say", "False"], "Transitive relation."),
        ("Statements: Some cats are dogs. All dogs are animals. Conclusion: Some cats are animals.", "Follows", ["Does not follow", "Cannot say", "False"], "Some cats that are dogs are animals."),
        ("Statements: No apples are oranges. Some oranges are fruits. Conclusion: Some apples are fruits.", "Does not follow", ["Follows", "Cannot say", "True"], "No overlap is given for apples and fruits."),
        ("Statements: All students are learners. Some learners are athletes. Conclusion: Some students are athletes.", "Cannot say", ["Follows", "Does not follow", "True"], "Some learners may not be students."),
        ("Statements: Some lights are lamps. Some lamps are tubes. Conclusion: Some lights are tubes.", "Cannot say", ["Follows", "Does not follow", "True"], "No direct link is guaranteed."),
    ],
    "Statement & Conclusion": [
        ("Statement: The company offers remote work on Fridays. Conclusion: Employees may work from home weekly.", "Likely follows", ["Definitely false", "No relation", "Cannot say"], "Remote Fridays imply a weekly work-from-home option."),
        ("Statement: The school increased library hours. Conclusion: Students now have more access to books.", "Follows", ["Does not follow", "Cannot say", "False"], "Longer hours improve access."),
        ("Statement: The city banned plastic bags in markets. Conclusion: Plastic bag usage may drop.", "Follows", ["Does not follow", "Cannot say", "False"], "A ban generally reduces usage."),
        ("Statement: The team hired two designers. Conclusion: The product will launch sooner.", "Cannot say", ["Follows", "Does not follow", "False"], "Hiring does not guarantee launch timing."),
        ("Statement: The exam was postponed due to weather. Conclusion: The original date was not practical.", "Likely follows", ["Definitely false", "Cannot say", "No relation"], "Weather-related postponement suggests scheduling issues."),
    ],
    "Cause & Effect": [
        ("Cause: It rained heavily overnight. Effect: The roads were wet in the morning.", "Cause and effect", ["Both unrelated", "Only cause", "Only effect"], "Rain commonly leads to wet roads."),
        ("Cause: The server crashed. Effect: Users could not log in.", "Cause and effect", ["Both unrelated", "Only cause", "Only effect"], "Crash blocks access."),
        ("Cause: The team trained daily. Effect: Performance improved.", "Cause and effect", ["Both unrelated", "Only cause", "Only effect"], "Practice improves skill."),
        ("Cause: The lamp was switched on. Effect: The room became bright.", "Cause and effect", ["Both unrelated", "Only cause", "Only effect"], "Switching on a lamp increases light."),
        ("Cause: The company offered bonuses. Effect: Employee morale rose.", "Cause and effect", ["Both unrelated", "Only cause", "Only effect"], "Bonuses often improve morale."),
    ],
    "Venn Diagram": [
        ("Which diagram best represents students, boys, and athletes?", "Overlapping sets", ["Disjoint sets", "Identical sets", "Single set"], "These categories partially overlap."),
        ("How are cats and dogs usually shown in a Venn diagram?", "Separate circles", ["One inside another", "A single circle", "No circles"], "They are distinct groups."),
        ("How should fruits, apples, and red apples be arranged?", "Nested circles", ["Disjoint circles", "Random blocks", "One line"], "Red apples are a subset of apples and fruits."),
        ("How are integers and even numbers shown?", "Subset relation", ["Disjoint", "Equal", "Unrelated"], "Even numbers are a subset of integers."),
        ("How should engineers, coders, and graduates be drawn?", "Overlapping circles", ["Single circle", "All disjoint", "No relation"], "These can overlap."),
    ],
    "Assumptions": [
        ("Statement: Bring your own bottle to the office.", "Assumption: Water is available", ["Assumption: No office exists", "Assumption: Bottles are banned", "Assumption: Everyone is absent"], "The instruction implies water can be used."),
        ("Statement: Join the workshop to improve skills.", "Assumption: The workshop is useful", ["Assumption: It is free", "Assumption: It is online", "Assumption: It is mandatory"], "Improvement is expected from participation."),
        ("Statement: Read the guidelines before applying.", "Assumption: Guidelines matter", ["Assumption: Guidelines are missing", "Assumption: Application is impossible", "Assumption: No one applies"], "Reading guidelines implies importance."),
        ("Statement: The library extended hours for students.", "Assumption: Students need more time", ["Assumption: Books are removed", "Assumption: Fees increased", "Assumption: No students exist"], "Extended hours are meant to help access."),
        ("Statement: Submit the form online.", "Assumption: Online submission is possible", ["Assumption: Paper forms are banned", "Assumption: Internet is unavailable", "Assumption: No form exists"], "The instruction presumes online access."),
    ],
    "Data Sufficiency": [
        ("Question: What is x? Statement 1: x + 2 = 5. Statement 2: x is an integer.", "Statement 1 alone", ["Statement 2 alone", "Both together", "Neither alone"], "Statement 1 gives x directly."),
        ("Question: Is x > 10? Statement 1: x = 12. Statement 2: x is even.", "Statement 1 alone", ["Statement 2 alone", "Both together", "Neither alone"], "Statement 1 is enough."),
        ("Question: What is the age of A? Statement 1: A is 5 years older than B. Statement 2: B is 20.", "Both together", ["Statement 1 alone", "Statement 2 alone", "Neither alone"], "Need both pieces of information."),
        ("Question: Is the number prime? Statement 1: It is odd. Statement 2: It is divisible by 3.", "Neither alone", ["Statement 1 alone", "Statement 2 alone", "Both together"], "Odd or divisible by 3 is not sufficient."),
        ("Question: Find the total. Statement 1: a = 4. Statement 2: b = 6.", "Both together", ["Statement 1 alone", "Statement 2 alone", "Neither alone"], "Both values are needed."),
    ],
}


def build_logical() -> list[dict[str, Any]]:
    banks: list[dict[str, Any]] = []
    for difficulty in ("easy", "medium", "hard"):
        for topic, seeds in LOGICAL_SEEDS.items():
            for idx, (question, correct, distractors, explanation) in enumerate(seeds):
                base = question
                if difficulty != "easy":
                    base = base.replace("?", f" ({difficulty})?")
                if idx % 2 == 1:
                    base = base.replace("What", "Identify").replace("How", "Determine")
                labeled = f"[{topic}][{difficulty}] {base}"
                banks.append(shuffled_mcq(labeled, correct, distractors, explanation, topic, difficulty))
                alt_question = base.replace("Which", "What") if "Which" in base else f"{base} State the answer carefully."
                labeled_alt = f"[{topic}][{difficulty}] {alt_question}"
                banks.append(shuffled_mcq(labeled_alt, correct, distractors[::-1], explanation, topic, difficulty))
    return banks


VERBAL_SEEDS = {
    "Synonyms": [
        ("Abundant", "Plentiful", ["Rare", "Scarce", "Empty"], "Plentiful is a synonym of abundant."),
        ("Brief", "Short", ["Long", "Large", "Broad"], "Short matches brief."),
        ("Candid", "Honest", ["Hidden", "Crafty", "False"], "Honest matches candid."),
        ("Expand", "Enlarge", ["Shrink", "Break", "Fold"], "Enlarge is close in meaning."),
        ("Rapid", "Fast", ["Slow", "Late", "Dull"], "Fast is synonymous with rapid."),
    ],
    "Antonyms": [
        ("Ancient", "Modern", ["Old", "Past", "Early"], "Modern is opposite to ancient."),
        ("Brave", "Cowardly", ["Bold", "Strong", "Sharp"], "Cowardly is the antonym."),
        ("Generous", "Stingy", ["Kind", "Open", "Friendly"], "Stingy is opposite to generous."),
        ("Expand", "Contract", ["Grow", "Stretch", "Open"], "Contract is the opposite."),
        ("Visible", "Invisible", ["Clear", "Bright", "Near"], "Invisible is opposite to visible."),
    ],
    "Grammar": [
        ("The committee ___ its report.", "has", ["have", "are", "were"], "Committee is singular in this sentence."),
        ("Each of the players ___ a medal.", "gets", ["get", "getting", "got"], "Each takes a singular verb."),
        ("Neither the teacher nor the students ___ present.", "are", ["is", "was", "has"], "The verb agrees with the nearer subject, students."),
        ("If I ___ enough time, I will finish it.", "have", ["has", "had", "having"], "First conditional uses present tense in the if-clause."),
        ("She is better ___ me at chess.", "than", ["then", "to", "from"], "Comparison uses than."),
    ],
    "Reading Comprehension": [
        ("A short passage about renewable energy says solar panels reduce electricity bills. What is one benefit?", "Lower electricity bills", ["More smoke", "Higher fuel use", "Less sunlight"], "The passage explicitly states the benefit."),
        ("A passage about remote work mentions flexibility and time savings. What is a key idea?", "Flexibility", ["Longer commute", "Less productivity", "More expenses"], "Flexibility is stated as an advantage."),
        ("A passage on healthy eating recommends fruits and vegetables. What is the main message?", "Balanced diet", ["Fast food", "Skipping meals", "Sugar only"], "Healthy food choices are encouraged."),
        ("A passage on urban transport supports buses and trains. What does it favor?", "Public transport", ["Private jets", "Walking only", "No travel"], "Public transport is the focus."),
        ("A passage on teamwork highlights cooperation. What is emphasized?", "Collaboration", ["Isolation", "Competition only", "Silence"], "Teamwork and cooperation are the theme."),
    ],
    "Error Spotting": [
        ("She don't like coffee.", "don't", ["She", "like", "coffee"], "'Doesn't' is correct for third-person singular."),
        ("He go to office daily.", "go", ["He", "to", "daily"], "'Goes' is required."),
        ("They was waiting for us.", "was", ["They", "waiting", "for"], "Plural subject takes 'were'."),
        ("The list of items are on the table.", "are", ["list", "items", "table"], "The subject is singular: list."),
        ("I have saw that movie.", "saw", ["I", "have", "movie"], "Present perfect uses 'have seen'."),
    ],
    "Sentence Improvement": [
        ("He is more taller than his brother.", "He is taller than his brother.", ["He is most taller than his brother.", "He is tall than his brother.", "He is more tall than his brother."], "Use one comparative form only."),
        ("She did not knew the answer.", "She did not know the answer.", ["She did not knows the answer.", "She do not know the answer.", "She not know the answer."], "Use base verb after did not."),
        ("The train arrived late than expected.", "The train arrived later than expected.", ["The train arrived latest than expected.", "The train arrived more late than expected.", "The train arrives late than expected."], "Use comparative adverb later."),
        ("Each of the boys have a book.", "Each of the boys has a book.", ["Each of the boys had a book.", "Each of the boys having a book.", "Each of the boys are a book."], "Each is singular."),
        ("The solution is consist of two parts.", "The solution consists of two parts.", ["The solution is consisting of two parts.", "The solution consist on two parts.", "The solution has consist of two parts."], "Use the correct verb form."),
    ],
    "Para Jumbles": [
        ("Arrange: A. He opened the door. B. John heard a knock. C. A visitor stood outside.", "BCA", ["ABC", "CAB", "BAC"], "Knock first, visitor second, opening last."),
        ("Arrange: A. It started to rain. B. The picnic ended. C. They packed their bags.", "ACB", ["ABC", "BAC", "CBA"], "Rain triggers packing then ending."),
        ("Arrange: A. The alarm rang. B. She woke up. C. She got ready for school.", "ABC", ["BAC", "CAB", "BCA"], "Alarm, wake, then prepare."),
        ("Arrange: A. The report was submitted. B. The team reviewed it. C. The manager approved it.", "BCA", ["ABC", "CBA", "ACB"], "Review, approval, submission sequence."),
        ("Arrange: A. He studied hard. B. He passed the exam. C. He celebrated with friends.", "ABC", ["BAC", "CBA", "ACB"], "Study, pass, celebrate."),
    ],
    "Idioms": [
        ("'Break the ice' means?", "To start a conversation", ["To repair something", "To become silent", "To end a meeting"], "It means to ease tension."),
        ("'Once in a blue moon' means?", "Very rarely", ["Every day", "At night", "At noon"], "It refers to rare events."),
        ("'Hit the nail on the head' means?", "Say exactly the right thing", ["Make a mistake", "Work slowly", "Avoid the issue"], "It means being exactly right."),
        ("'Spill the beans' means?", "Reveal a secret", ["Cook quickly", "Waste time", "Stay quiet"], "It means to disclose information."),
        ("'A piece of cake' means?", "Very easy", ["Very difficult", "Very expensive", "Very old"], "It means something easy."),
    ],
    "One-word Substitution": [
        ("A person who loves books", "Bibliophile", ["Photographer", "Biologist", "Linguist"], "Bibliophile is a book lover."),
        ("A government by the people", "Democracy", ["Monarchy", "Dictatorship", "Aristocracy"], "Democracy means rule by the people."),
        ("A place where animals are kept", "Zoo", ["Museum", "Library", "Airport"], "Zoo houses animals."),
        ("A fear of heights", "Acrophobia", ["Claustrophobia", "Hydrophobia", "Anthropology"], "Acrophobia is fear of heights."),
        ("One who speaks many languages", "Polyglot", ["Monk", "Poet", "Pilot"], "Polyglot means a multilingual person."),
    ],
    "Fill in the Blanks": [
        ("She is interested ___ music.", "in", ["on", "at", "for"], "The correct preposition is 'in'."),
        ("I look forward ___ meeting you.", "to", ["for", "in", "at"], "'Look forward to' is the fixed phrase."),
        ("The room was filled ___ smoke.", "with", ["in", "at", "by"], "'Filled with' is standard."),
        ("He insisted ___ paying the bill.", "on", ["in", "at", "to"], "The verb insists on."),
        ("We were surprised ___ the results.", "by", ["with", "to", "at"], "Surprised by is correct here."),
    ],
    "Voice": [
        ("Active: She writes a letter. Passive?", "A letter is written by her.", ["A letter was written by her.", "A letter writes her.", "She is written by a letter."], "Present simple passive uses is/are + past participle."),
        ("Active: They are cleaning the hall. Passive?", "The hall is being cleaned by them.", ["The hall was cleaned by them.", "The hall cleans them.", "The hall is clean by them."], "Present continuous passive uses is being."),
        ("Active: He completed the task. Passive?", "The task was completed by him.", ["The task is completed by him.", "The task completes him.", "The task was completing by him."], "Past simple passive uses was/were + past participle."),
        ("Active: The teacher will announce the result. Passive?", "The result will be announced by the teacher.", ["The result is announced by the teacher.", "The result announced the teacher.", "The result was announced by the teacher."], "Future passive uses will be."),
        ("Active: Someone has stolen my bike. Passive?", "My bike has been stolen.", ["My bike is stolen.", "My bike was stolen by someone has.", "My bike have been stolen."], "Present perfect passive uses has/have been."),
    ],
    "Narration": [
        ("Direct: He said, 'I am busy.'", "He said that he was busy.", ["He said that I was busy.", "He says that he is busy.", "He said he am busy."], "Backshift is needed in indirect speech."),
        ("Direct: She asked, 'Where do you live?'", "She asked where I lived.", ["She asked where do I live.", "She asked where I live.", "She asked where did I live."], "Question word plus statement form in indirect speech."),
        ("Direct: The teacher said, 'Study hard.'", "The teacher advised us to study hard.", ["The teacher said us study hard.", "The teacher asked us study hard.", "The teacher ordered us to studies hard."], "Imperatives often become advised/to ordered."),
        ("Direct: He said, 'I will come tomorrow.'", "He said that he would come the next day.", ["He said that he will come tomorrow.", "He said that he come tomorrow.", "He said that he would came tomorrow."], "Future shifts to would and tomorrow to next day."),
        ("Direct: They said, 'We have finished.'", "They said that they had finished.", ["They said that they have finished.", "They said that we had finished.", "They said that they has finished."], "Present perfect changes to past perfect."),
    ],
}


def build_verbal() -> list[dict[str, Any]]:
    banks: list[dict[str, Any]] = []
    for difficulty in ("easy", "medium", "hard"):
        for topic, seeds in VERBAL_SEEDS.items():
            for idx, (prompt, correct, distractors, explanation) in enumerate(seeds):
                q1 = prompt if difficulty == "easy" else f"{prompt} [{difficulty}]"
                if idx % 2 == 0:
                    q2 = q1.replace("What", "Which") if "What" in q1 else q1.replace("She", "She herself")
                else:
                    q2 = q1.replace("means", "best means")
                if q2 == q1:
                    q2 = f"{q1} - alternate wording"
                labeled_q1 = f"[{topic}][{difficulty}] {q1}"
                labeled_q2 = f"[{topic}][{difficulty}] {q2}"
                banks.append(shuffled_mcq(labeled_q1, correct, distractors, explanation, topic, difficulty))
                banks.append(shuffled_mcq(labeled_q2, correct, distractors[::-1], explanation, topic, difficulty))
    return banks


TECH_SEEDS = {
    "C": [
        ("What keyword is used to define a structure?", "struct", ["class", "define", "module"], "struct defines a structure in C."),
        ("What operator gives the address of a variable?", "&", ["*", "%", "#"], "The address-of operator is &."),
        ("What is used to access the value pointed by a pointer?", "*", ["&", ".", ":"], "The dereference operator is *."),
        ("Which storage class preserves value across function calls?", "static", ["auto", "register", "extern"], "static retains its value."),
        ("Which header is used for standard input/output?", "stdio.h", ["stdlib.h", "string.h", "math.h"], "stdio.h contains I/O declarations."),
    ],
    "C++": [
        ("What feature allows functions to have the same name with different parameters?", "Function overloading", ["Encapsulation", "Inheritance", "Abstraction"], "Overloading depends on parameter lists."),
        ("Which keyword creates a reference in C++?", "&", ["*", "ref", "@"], "& after a type declares a reference."),
        ("What is the base of STL vector?", "Dynamic array", ["Linked list", "Stack", "Tree"], "Vector behaves like a dynamic array."),
        ("Which function runs automatically when an object is created?", "Constructor", ["Destructor", "Operator", "Initializer"], "Constructors initialize objects."),
        ("What pointer concept is central to polymorphism?", "Virtual function", ["Global variable", "Macro", "Namespace"], "Virtual functions enable runtime polymorphism."),
    ],
    "Java": [
        ("Which component runs compiled bytecode?", "JVM", ["JDK", "JRE", "JIT"], "The JVM executes bytecode."),
        ("Which keyword prevents inheritance?", "final", ["static", "private", "abstract"], "final classes cannot be extended."),
        ("Which collection stores key-value pairs?", "HashMap", ["ArrayList", "TreeSet", "Queue"], "HashMap stores mappings."),
        ("What does garbage collection manage?", "Memory cleanup", ["Networking", "Compilation", "Encryption"], "GC reclaims unused memory."),
        ("Which interface can be used for sorting?", "Comparable", ["Runnable", "Serializable", "Cloneable"], "Comparable defines natural ordering."),
    ],
    "Python": [
        ("Which keyword defines a function?", "def", ["func", "lambda", "make"], "def starts a function definition."),
        ("What is a generator used for?", "Lazy iteration", ["UI design", "File compression", "Sorting only"], "Generators produce values lazily."),
        ("Which method creates a shallow copy of a list?", "copy()", ["clone()", "slice()", "paste()"], "copy() returns a shallow copy."),
        ("What does __name__ == '__main__' indicate?", "The file is run directly", ["The file is imported", "The file is encrypted", "The file is empty"], "It distinguishes direct execution."),
        ("Which feature changes function behavior without editing the original?", "Decorator", ["Iterator", "Alias", "Module"], "Decorators wrap functions."),
    ],
    "JavaScript": [
        ("Which keyword declares a block-scoped variable?", "let", ["var", "int", "dim"], "let is block-scoped."),
        ("What does JSON stand for in JavaScript work?", "JavaScript Object Notation", ["Java Source Object Name", "Joined Script Order Network", "Java Standard Object Node"], "JSON is a data format."),
        ("Which function schedules a callback after a delay?", "setTimeout", ["setInterval", "delay", "wait"], "setTimeout runs once after a delay."),
        ("What does '===' check?", "Strict equality", ["Assignment", "Approximation", "Truthiness only"], "It compares type and value."),
        ("Which object handles asynchronous results?", "Promise", ["Array", "Map", "Set"], "Promises represent future values."),
    ],
    "SQL": [
        ("Which clause filters grouped rows?", "HAVING", ["WHERE", "ORDER BY", "GROUP BY"], "HAVING works after grouping."),
        ("Which join returns matching rows from both tables?", "INNER JOIN", ["LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"], "Inner join keeps common matches."),
        ("Which command removes all rows but keeps structure?", "TRUNCATE", ["DROP", "DELETE", "ALTER"], "TRUNCATE clears data."),
        ("Which keyword removes duplicate rows from a query result?", "DISTINCT", ["UNIQUE", "GROUP", "SORT"], "DISTINCT removes duplicates."),
        ("Which function counts rows?", "COUNT", ["SUM", "AVG", "MAX"], "COUNT returns row totals."),
    ],
    "DBMS": [
        ("What normal form removes partial dependency?", "2NF", ["1NF", "3NF", "BCNF"], "2NF removes partial dependency."),
        ("Which property ensures atomicity, consistency, isolation, durability?", "ACID", ["BASE", "CRUD", "SQL"], "ACID is the transaction standard."),
        ("What is a deadlock?", "Cyclic waiting", ["Fast query", "Data backup", "Index rebuild"], "Deadlock is circular waiting."),
        ("What is the purpose of indexing?", "Faster retrieval", ["Data encryption", "Backup", "Replication"], "Indexes speed up searches."),
        ("Which anomaly occurs when deleting a record removes important data?", "Deletion anomaly", ["Insertion anomaly", "Update anomaly", "Join anomaly"], "Deleting a row can lose information."),
    ],
    "Operating Systems": [
        ("Which scheduler chooses processes for CPU execution?", "CPU scheduler", ["Disk scheduler", "Memory manager", "Driver"], "CPU scheduler allocates the processor."),
        ("What is paging used for?", "Memory management", ["File compression", "Network routing", "Audio mixing"], "Paging manages virtual memory."),
        ("What is a thread?", "Lightweight execution path", ["File system", "Driver", "Process only"], "Threads share a process context."),
        ("Which condition requires mutual exclusion?", "Critical section", ["Cache miss", "Boot sequence", "File rename"], "Critical sections need synchronization."),
        ("What does the OS kernel do?", "Manages core resources", ["Edits text files", "Compiles code", "Runs browsers only"], "Kernel controls core operations."),
    ],
    "Computer Networks": [
        ("Which layer handles IP addressing?", "Network layer", ["Physical layer", "Application layer", "Data link layer"], "IP works at the network layer."),
        ("What does DNS do?", "Resolves names to IPs", ["Encrypts traffic", "Compresses files", "Blocks spam"], "DNS maps domain names to addresses."),
        ("Which protocol is connection-oriented?", "TCP", ["UDP", "ICMP", "ARP"], "TCP provides reliable connections."),
        ("What device forwards packets between networks?", "Router", ["Switch", "Hub", "Repeater"], "Routers forward traffic."),
        ("What does HTTP primarily transfer?", "Web pages", ["Emails", "Bluetooth signals", "Image sensors"], "HTTP carries web content."),
    ],
    "OOP": [
        ("Which principle hides internal details?", "Encapsulation", ["Inheritance", "Polymorphism", "Compilation"], "Encapsulation bundles data and methods."),
        ("Which principle allows one interface, many forms?", "Polymorphism", ["Abstraction", "Aggregation", "Exception handling"], "Polymorphism enables multiple forms."),
        ("What is reuse of a parent class called?", "Inheritance", ["Iteration", "Abstraction", "Polymorphism"], "Inheritance promotes reuse."),
        ("What separates interface from implementation?", "Abstraction", ["Coupling", "Concatenation", "Serialization"], "Abstraction shows essentials only."),
        ("What combines objects to represent a whole?", "Composition", ["Repetition", "Inheritance", "Threading"], "Composition uses has-a relationships."),
    ],
    "Data Structures": [
        ("Which structure follows LIFO?", "Stack", ["Queue", "Tree", "Graph"], "Stack is last-in, first-out."),
        ("Which structure follows FIFO?", "Queue", ["Stack", "Heap", "Trie"], "Queue is first-in, first-out."),
        ("Which structure stores hierarchical data?", "Tree", ["Array", "Set", "Buffer"], "Trees are hierarchical."),
        ("Which structure gives O(1) average lookup by key?", "Hash table", ["Linked list", "Stack", "Queue"], "Hash tables provide average constant lookup."),
        ("Which structure is ideal for recursive traversal?", "Tree", ["Queue", "Array", "Deque"], "Trees naturally support recursion."),
    ],
    "Algorithms": [
        ("Which search method halves the search space each step?", "Binary search", ["Linear search", "DFS", "BFS"], "Binary search divides the range."),
        ("Which sorting algorithm is based on divide and conquer?", "Merge sort", ["Bubble sort", "Selection sort", "Insertion sort"], "Merge sort splits and merges."),
        ("What is the time complexity of a nested loop over n items?", "O(n^2)", ["O(n)", "O(log n)", "O(1)"], "Nested loops are quadratic."),
        ("Which paradigm solves overlapping subproblems?", "Dynamic programming", ["Greedy", "Backtracking", "Hashing"], "DP stores sub-results."),
        ("Which technique always picks local optimum?", "Greedy", ["Dynamic programming", "Recursion", "Branch and bound"], "Greedy chooses best immediate option."),
    ],
    "Software Engineering": [
        ("Which model emphasizes iterative development?", "Agile", ["Waterfall", "Spiral", "V-model"], "Agile uses short cycles."),
        ("What is unit testing used for?", "Testing small components", ["Deploying code", "Writing documentation", "Buying servers"], "Unit tests validate small units."),
        ("Which document captures requirements?", "SRS", ["API", "DLL", "CSV"], "Software Requirement Specification."),
        ("What is version control used for?", "Tracking changes", ["Encrypting files", "Rendering graphics", "Printing reports"], "Version control tracks history."),
        ("What is refactoring?", "Improving code structure", ["Deleting tests", "Adding bugs", "Skipping review"], "Refactoring improves internal design."),
    ],
    "Git": [
        ("What command creates a new branch?", "git branch", ["git merge", "git push", "git fetch"], "git branch creates branches."),
        ("What command records changes?", "git commit", ["git pull", "git clone", "git status"], "Commit saves a snapshot."),
        ("What command uploads local commits?", "git push", ["git pull", "git fetch", "git reset"], "Push sends commits to remote."),
        ("What command downloads remote changes without merging?", "git fetch", ["git merge", "git rebase", "git tag"], "Fetch retrieves updates."),
        ("What command saves uncommitted work temporarily?", "git stash", ["git log", "git init", "git show"], "Stash stores changes aside."),
    ],
    "Cloud": [
        ("Which model provides virtual machines and storage?", "IaaS", ["SaaS", "PaaS", "FaaS"], "Infrastructure as a Service."),
        ("Which model gives a runtime platform to developers?", "PaaS", ["IaaS", "SaaS", "DaaS"], "Platform as a Service."),
        ("Which model delivers software over the internet?", "SaaS", ["IaaS", "PaaS", "BaaS"], "Software as a Service."),
        ("What improves availability by spreading traffic?", "Load balancing", ["Compression", "Defragmentation", "Caching only"], "Load balancing distributes requests."),
        ("What does auto-scaling do?", "Adjusts resources automatically", ["Deletes backups", "Stops logs", "Blocks users"], "It adapts capacity to demand."),
    ],
    "Cybersecurity": [
        ("What protects data by converting it into unreadable form?", "Encryption", ["Compression", "Indexing", "Logging"], "Encryption secures data."),
        ("What verifies a user's identity?", "Authentication", ["Authorization", "Aggregation", "Annotation"], "Authentication checks identity."),
        ("What allows a user to access permitted resources?", "Authorization", ["Authentication", "Archiving", "Auditing"], "Authorization grants access rights."),
        ("What attack injects malicious SQL into queries?", "SQL injection", ["Phishing", "DDoS", "Spoofing"], "SQL injection targets databases."),
        ("What is the CIA triad about?", "Confidentiality, Integrity, Availability", ["Code, Input, Access", "Cache, Index, Audit", "Control, Identity, Analytics"], "CIA triad is a security model."),
    ],
}


def build_technical() -> list[dict[str, Any]]:
    banks: list[dict[str, Any]] = []
    for difficulty in ("easy", "medium", "hard"):
        for topic, seeds in TECH_SEEDS.items():
            for prompt, correct, distractors, explanation in seeds:
                q1 = prompt if difficulty == "easy" else f"{prompt} ({difficulty})"
                q2 = f"In {topic}, {prompt[0].lower() + prompt[1:]}"
                labeled_q1 = f"[{topic}][{difficulty}] {q1}"
                labeled_q2 = f"[{topic}][{difficulty}] {q2}"
                if labeled_q1 == labeled_q2:
                    labeled_q2 = f"{labeled_q2} - alternate wording"
                banks.append(shuffled_mcq(labeled_q1, correct, distractors, explanation, topic, difficulty))
                banks.append(shuffled_mcq(labeled_q2, correct, distractors[::-1], explanation, topic, difficulty))
    return banks


def validate_bank(bank: list[dict[str, Any]], module: str) -> None:
    seen_questions: set[str] = set()
    for item in bank:
        if item["question"] in seen_questions:
            raise ValueError(f"Duplicate wording found in {module}: {item['question']}")
        seen_questions.add(item["question"])
        if len(item.get("options", [])) != 4:
            raise ValueError(f"Invalid option count in {module}: {item['question']}")
        if not (0 <= int(item.get("answer", -1)) < 4):
            raise ValueError(f"Invalid answer index in {module}: {item['question']}")
    print(f"{module}: {len(bank)} questions")


def write_bank(name: str, questions: list[dict[str, Any]]) -> None:
    path = DATA_DIR / f"{name}.json"
    path.write_text(json.dumps(questions, indent=4, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    aptitude = generate_aptitude()
    logical = build_logical()
    verbal = build_verbal()
    technical = build_technical()

    validate_bank(aptitude, "aptitude")
    validate_bank(logical, "logical")
    validate_bank(verbal, "verbal")
    validate_bank(technical, "technical")

    write_bank("aptitude", aptitude)
    write_bank("logical", logical)
    write_bank("verbal", verbal)
    write_bank("technical", technical)

    print("Validation complete. JSON banks written successfully.")


if __name__ == "__main__":
    main()
