CODING_QUESTION_BANK = {
    "easy": [
        {
            "id": "two_sum",
            "title": "Two Sum",
            "difficulty": "Easy",
            "problem_statement": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
            "examples": [
                {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."}
            ],
            "constraints": [
                "2 <= nums.length <= 10^4",
                "-10^9 <= nums[i] <= 10^9",
                "-10^9 <= target <= 10^9"
            ],
            "starter_code": {
                "Python": "def two_sum(nums, target):\n    # Write your code here\n    return []",
                "Java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}",
                "C++": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n        return {};\n    }\n};",
                "JavaScript": "function twoSum(nums, target) {\n    // Write your code here\n    return [];\n}"
            },
            "hidden_test_cases": [
                {"input": "[2,7,11,15], target = 9", "expected": "[0,1]"},
                {"input": "[3,2,4], target = 6", "expected": "[1,2]"},
                {"input": "[3,3], target = 6", "expected": "[0,1]"}
            ]
        },
        {
            "id": "palindrome_number",
            "title": "Palindrome Number",
            "difficulty": "Easy",
            "problem_statement": "Given an integer `x`, return `true` if `x` is a palindrome, and `false` otherwise. An integer is a palindrome when it reads the same backward as forward.",
            "examples": [
                {"input": "x = 121", "output": "true", "explanation": "121 reads as 121 from left to right and from right to left."}
            ],
            "constraints": [
                "-2^31 <= x <= 2^31 - 1"
            ],
            "starter_code": {
                "Python": "def is_palindrome(x):\n    # Write your code here\n    return False",
                "Java": "class Solution {\n    public boolean isPalindrome(int x) {\n        // Write your code here\n        return false;\n    }\n}",
                "C++": "class Solution {\npublic:\n    bool isPalindrome(int x) {\n        // Write your code here\n        return false;\n    }\n};",
                "JavaScript": "function isPalindrome(x) {\n    // Write your code here\n    return false;\n}"
            },
            "hidden_test_cases": [
                {"input": "121", "expected": "true"},
                {"input": "-121", "expected": "false"},
                {"input": "10", "expected": "false"}
            ]
        },
        {
            "id": "valid_parentheses",
            "title": "Valid Parentheses",
            "difficulty": "Easy",
            "problem_statement": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if brackets close in the correct order and are of the same type.",
            "examples": [
                {"input": "s = '()[]{}'", "output": "true", "explanation": "All brackets close properly in order."}
            ],
            "constraints": [
                "1 <= s.length <= 10^4",
                "s consists of parentheses only."
            ],
            "starter_code": {
                "Python": "def is_valid(s):\n    # Write your code here\n    return False",
                "Java": "class Solution {\n    public boolean isValid(String s) {\n        // Write your code here\n        return false;\n    }\n}",
                "C++": "class Solution {\npublic:\n    bool isValid(string s) {\n        // Write your code here\n        return false;\n    }\n};",
                "JavaScript": "function isValid(s) {\n    // Write your code here\n    return false;\n}"
            },
            "hidden_test_cases": [
                {"input": "\"()\"", "expected": "true"},
                {"input": "\"()[]{}\"", "expected": "true"},
                {"input": "\"(]\"", "expected": "false"}
            ]
        },
        {
            "id": "reverse_string",
            "title": "Reverse String",
            "difficulty": "Easy",
            "problem_statement": "Write a function that reverses a string. The input string is given as an array of characters `s`. You must do this by modifying the input array in-place with O(1) extra memory.",
            "examples": [
                {"input": "s = ['h','e','l','l','o']", "output": "['o','l','l','e','h']", "explanation": "The array is reversed in-place."}
            ],
            "constraints": [
                "1 <= s.length <= 10^5",
                "s[i] is a printable ascii character."
            ],
            "starter_code": {
                "Python": "def reverse_string(s):\n    # Write your code here\n    pass",
                "Java": "class Solution {\n    public void reverseString(char[] s) {\n        // Write your code here\n    }\n}",
                "C++": "class Solution {\npublic:\n    void reverseString(vector<char>& s) {\n        // Write your code here\n    }\n};",
                "JavaScript": "function reverseString(s) {\n    // Write your code here\n}"
            },
            "hidden_test_cases": [
                {"input": "[\"h\",\"e\",\"l\",\"l\",\"o\"]", "expected": "[\"o\",\"l\",\"l\",\"e\",\"h\"]"},
                {"input": "[\"H\",\"a\",\"n\",\"n\",\"a\",\"h\"]", "expected": "[\"h\",\"a\",\"n\",\"n\",\"a\",\"H\"]"}
            ]
        },
        {
            "id": "merge_arrays",
            "title": "Merge Arrays",
            "difficulty": "Easy",
            "problem_statement": "Given two sorted integer arrays `nums1` and `nums2`, merge `nums2` into `nums1` as one sorted array. `nums1` has size `m + n` where the first `m` elements denote the elements that should be merged, and the last `n` elements are set to 0.",
            "examples": [
                {"input": "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3", "output": "[1,2,2,3,5,6]", "explanation": "The arrays are merged into nums1."}
            ],
            "constraints": [
                "nums1.length == m + n",
                "nums2.length == n",
                "0 <= m, n <= 200"
            ],
            "starter_code": {
                "Python": "def merge(nums1, m, nums2, n):\n    # Write your code here\n    pass",
                "Java": "class Solution {\n    public void merge(int[] nums1, int m, int[] nums2, int n) {\n        // Write your code here\n    }\n}",
                "C++": "class Solution {\npublic:\n    void merge(vector<int>& nums1, int m, vector<int>& nums2, int n) {\n        // Write your code here\n    }\n};",
                "JavaScript": "function merge(nums1, m, nums2, n) {\n    // Write your code here\n}"
            },
            "hidden_test_cases": [
                {"input": "nums1 = [1,2,3,0,0,0], m = 3, nums2 = [2,5,6], n = 3", "expected": "[1,2,2,3,5,6]"},
                {"input": "nums1 = [1], m = 1, nums2 = [], n = 0", "expected": "[1]"}
            ]
        }
    ],
    "medium": [
        {
            "id": "longest_substring",
            "title": "Longest Substring Without Repeating Characters",
            "difficulty": "Medium",
            "problem_statement": "Given a string `s`, find the length of the longest substring without repeating characters.",
            "examples": [
                {"input": "s = 'abcabcbb'", "output": "3", "explanation": "The answer is 'abc', with the length of 3."}
            ],
            "constraints": [
                "0 <= s.length <= 5 * 10^4",
                "s consists of English letters, digits, symbols and spaces."
            ],
            "starter_code": {
                "Python": "def length_of_longest_substring(s):\n    # Write your code here\n    return 0",
                "Java": "class Solution {\n    public int lengthOfLongestSubstring(String s) {\n        // Write your code here\n        return 0;\n    }\n}",
                "C++": "class Solution {\npublic:\n    int lengthOfLongestSubstring(string s) {\n        // Write your code here\n        return 0;\n    }\n};",
                "JavaScript": "function lengthOfLongestSubstring(s) {\n    // Write your code here\n    return 0;\n}"
            },
            "hidden_test_cases": [
                {"input": "\"abcabcbb\"", "expected": "3"},
                {"input": "\"bbbbb\"", "expected": "1"},
                {"input": "\"pwwkew\"", "expected": "3"}
            ]
        },
        {
            "id": "group_anagrams",
            "title": "Group Anagrams",
            "difficulty": "Medium",
            "problem_statement": "Given an array of strings `strs`, group the anagrams together. You can return the answer in any order. An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase.",
            "examples": [
                {"input": "strs = ['eat','tea','tan','ate','nat','bat']", "output": "[['bat'],['nat','tan'],['ate','eat','tea']]", "explanation": "Anagram groups are identified."}
            ],
            "constraints": [
                "1 <= strs.length <= 10^4",
                "0 <= strs[i].length <= 100"
            ],
            "starter_code": {
                "Python": "def group_anagrams(strs):\n    # Write your code here\n    return []",
                "Java": "class Solution {\n    public List<List<String>> groupAnagrams(String[] strs) {\n        // Write your code here\n        return new ArrayList<>();\n    }\n}",
                "C++": "class Solution {\npublic:\n    vector<vector<string>> groupAnagrams(vector<string>& strs) {\n        // Write your code here\n        return {};\n    }\n};",
                "JavaScript": "function groupAnagrams(strs) {\n    // Write your code here\n    return [];\n}"
            },
            "hidden_test_cases": [
                {"input": "[\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "expected": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]"},
                {"input": "[\"\"]", "expected": "[[\"\"]]"},
                {"input": "[\"a\"]", "expected": "[[\"a\"]]"}
            ]
        },
        {
            "id": "binary_search_tree",
            "title": "Validate Binary Search Tree",
            "difficulty": "Medium",
            "problem_statement": "Given the root of a binary tree, determine if it is a valid binary search tree (BST). A valid BST is defined as: the left subtree of a node contains only nodes with keys less than the node's key; the right subtree contains only nodes with keys greater than the node's key; both left and right subtrees must also be binary search trees.",
            "examples": [
                {"input": "root = [2,1,3]", "output": "true", "explanation": "The root value is 2, left is 1 (less than 2), right is 3 (greater than 2)."}
            ],
            "constraints": [
                "The number of nodes in the tree is in the range [1, 10^4].",
                "-2^31 <= Node.val <= 2^31 - 1"
            ],
            "starter_code": {
                "Python": "def isValidBST(root):\n    # Write your code here\n    return True",
                "Java": "class Solution {\n    public boolean isValidBST(TreeNode root) {\n        // Write your code here\n        return true;\n    }\n}",
                "C++": "class Solution {\npublic:\n    bool isValidBST(TreeNode* root) {\n        // Write your code here\n        return true;\n    }\n};",
                "JavaScript": "function isValidBST(root) {\n    // Write your code here\n    return true;\n}"
            },
            "hidden_test_cases": [
                {"input": "[2,1,3]", "expected": "true"},
                {"input": "[5,1,4,null,null,3,6]", "expected": "false"}
            ]
        },
        {
            "id": "top_k_elements",
            "title": "Top K Frequent Elements",
            "difficulty": "Medium",
            "problem_statement": "Given an integer array `nums` and an integer `k`, return the `k` most frequent elements. You may return the answer in any order.",
            "examples": [
                {"input": "nums = [1,1,1,2,2,3], k = 2", "output": "[1,2]", "explanation": "1 appears 3 times, 2 appears 2 times, so top 2 is [1,2]."}
            ],
            "constraints": [
                "1 <= nums.length <= 10^5",
                "-10^4 <= nums[i] <= 10^4",
                "k is in the range [1, the number of unique elements in the array]."
            ],
            "starter_code": {
                "Python": "def top_k_frequent(nums, k):\n    # Write your code here\n    return []",
                "Java": "class Solution {\n    public int[] topKFrequent(int[] nums, int k) {\n        // Write your code here\n        return new int[0];\n    }\n}",
                "C++": "class Solution {\npublic:\n    vector<int> topKFrequent(vector<int>& nums, int k) {\n        // Write your code here\n        return {};\n    }\n};",
                "JavaScript": "function topKFrequent(nums, k) {\n    // Write your code here\n    return [];\n}"
            },
            "hidden_test_cases": [
                {"input": "[1,1,1,2,2,3], k = 2", "expected": "[1,2]"},
                {"input": "[1], k = 1", "expected": "[1]"}
            ]
        },
        {
            "id": "spiral_matrix",
            "title": "Spiral Matrix",
            "difficulty": "Medium",
            "problem_statement": "Given an `m x n` matrix, return all elements of the matrix in spiral order.",
            "examples": [
                {"input": "matrix = [[1,2,3],[4,5,6],[7,8,9]]", "output": "[1,2,3,6,9,8,7,4,5]", "explanation": "Traversing the matrix in spiral path gives the output."}
            ],
            "constraints": [
                "m == matrix.length",
                "n == matrix[i].length",
                "1 <= m, n <= 10"
            ],
            "starter_code": {
                "Python": "def spiral_order(matrix):\n    # Write your code here\n    return []",
                "Java": "class Solution {\n    public List<Integer> spiralOrder(int[][] matrix) {\n        // Write your code here\n        return new ArrayList<>();\n    }\n}",
                "C++": "class Solution {\npublic:\n    vector<int> spiralOrder(vector<vector<int>>& matrix) {\n        // Write your code here\n        return {};\n    }\n};",
                "JavaScript": "function spiralOrder(matrix) {\n    // Write your code here\n    return [];\n}"
            },
            "hidden_test_cases": [
                {"input": "[[1,2,3],[4,5,6],[7,8,9]]", "expected": "[1,2,3,6,9,8,7,4,5]"},
                {"input": "[[1,2,3,4],[5,6,7,8],[9,10,11,12]]", "expected": "[1,2,3,4,8,12,11,10,9,5,6,7]"}
            ]
        }
    ],
    "hard": [
        {
            "id": "lru_cache",
            "title": "LRU Cache",
            "difficulty": "Hard",
            "problem_statement": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache. Implement the `LRUCache` class with `get(key)` and `put(key, value)` operations in O(1) time complexity.",
            "examples": [
                {"input": "LRUCache cache = new LRUCache(2); cache.put(1,1); cache.get(1);", "output": "1", "explanation": "Cache successfully stores and retrieves key 1."}
            ],
            "constraints": [
                "1 <= capacity <= 3000",
                "0 <= key <= 10^4",
                "0 <= value <= 10^5"
            ],
            "starter_code": {
                "Python": "class LRUCache:\n    def __init__(self, capacity: int):\n        pass\n    def get(self, key: int) -> int:\n        return -1\n    def put(self, key: int, value: int) -> None:\n        pass",
                "Java": "class LRUCache {\n    public LRUCache(int capacity) {}\n    public int get(int key) { return -1; }\n    public void put(int key, int value) {}\n}",
                "C++": "class LRUCache {\npublic:\n    LRUCache(int capacity) {}\n    int get(int key) { return -1; }\n    void put(int key, int value) {}\n};",
                "JavaScript": "class LRUCache {\n    constructor(capacity) {}\n    get(key) { return -1; }\n    put(key, value) {}\n}"
            },
            "hidden_test_cases": [
                {"input": "capacity=2, actions=['put', 'put', 'get', 'put', 'get'], args=[[1,1],[2,2],[1],[3,3],[2]]", "expected": "[null,null,1,null,-1]"}
            ]
        },
        {
            "id": "median_two_arrays",
            "title": "Median of Two Sorted Arrays",
            "difficulty": "Hard",
            "problem_statement": "Given two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the median of the two sorted arrays. The overall run time complexity should be O(log (m+n)).",
            "examples": [
                {"input": "nums1 = [1,3], nums2 = [2]", "output": "2.0", "explanation": "The merged array is [1,2,3] and median is 2.0."}
            ],
            "constraints": [
                "nums1.length == m, nums2.length == n",
                "0 <= m, n <= 1000"
            ],
            "starter_code": {
                "Python": "def find_median_sorted_arrays(nums1, nums2):\n    # Write your code here\n    return 0.0",
                "Java": "class Solution {\n    public double findMedianSortedArrays(int[] nums1, int[] nums2) {\n        // Write your code here\n        return 0.0;\n    }\n}",
                "C++": "class Solution {\npublic:\n    double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2) {\n        // Write your code here\n        return 0.0;\n    }\n};",
                "JavaScript": "function findMedianSortedArrays(nums1, nums2) {\n    // Write your code here\n    return 0.0;\n}"
            },
            "hidden_test_cases": [
                {"input": "nums1=[1,3], nums2=[2]", "expected": "2.0"},
                {"input": "nums1=[1,2], nums2=[3,4]", "expected": "2.5"}
            ]
        },
        {
            "id": "word_ladder",
            "title": "Word Ladder",
            "difficulty": "Hard",
            "problem_statement": "Given two words, `beginWord` and `endWord`, and a dictionary `wordList`, return the number of words in the shortest transformation sequence from `beginWord` to `endWord`, such that only one letter can be changed at a time and each intermediate word must exist in `wordList`.",
            "examples": [
                {"input": "beginWord = 'hit', endWord = 'cog', wordList = ['hot','dot','dog','lot','log','cog']", "output": "5", "explanation": "hit -> hot -> dot -> dog -> cog is 5 words."}
            ],
            "constraints": [
                "1 <= beginWord.length <= 10",
                "wordList.length <= 5000"
            ],
            "starter_code": {
                "Python": "def ladder_length(beginWord, endWord, wordList):\n    # Write your code here\n    return 0",
                "Java": "class Solution {\n    public int ladderLength(String beginWord, String endWord, List<String> wordList) {\n        // Write your code here\n        return 0;\n    }\n}",
                "C++": "class Solution {\npublic:\n    int ladderLength(string beginWord, string endWord, vector<string>& wordList) {\n        // Write your code here\n        return 0;\n    }\n};",
                "JavaScript": "function ladderLength(beginWord, endWord, wordList) {\n    // Write your code here\n    return 0;\n}"
            },
            "hidden_test_cases": [
                {"input": "beginWord=\"hit\", endWord=\"cog\", wordList=[\"hot\",\"dot\",\"dog\",\"lot\",\"log\",\"cog\"]", "expected": "5"},
                {"input": "beginWord=\"hit\", endWord=\"cog\", wordList=[\"hot\",\"dot\",\"dog\",\"lot\",\"log\"]", "expected": "0"}
            ]
        },
        {
            "id": "merge_k_lists",
            "title": "Merge k Sorted Lists",
            "difficulty": "Hard",
            "problem_statement": "You are given an array of `k` linked-lists `lists`, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.",
            "examples": [
                {"input": "lists = [[1,4,5],[1,3,4],[2,6]]", "output": "[1,1,2,3,4,4,5,6]", "explanation": "Lists are merged into a single sorted list."}
            ],
            "constraints": [
                "k == lists.length",
                "0 <= k <= 10^4",
                "0 <= lists[i].length <= 500"
            ],
            "starter_code": {
                "Python": "def mergeKLists(lists):\n    # Write your code here\n    return None",
                "Java": "class Solution {\n    public ListNode mergeKLists(ListNode[] lists) {\n        // Write your code here\n        return null;\n    }\n}",
                "C++": "class Solution {\npublic:\n    ListNode* mergeKLists(vector<ListNode*>& lists) {\n        // Write your code here\n        return nullptr;\n    }\n};",
                "JavaScript": "function mergeKLists(lists) {\n    // Write your code here\n    return null;\n}"
            },
            "hidden_test_cases": [
                {"input": "[[1,4,5],[1,3,4],[2,6]]", "expected": "[1,1,2,3,4,4,5,6]"},
                {"input": "[]", "expected": "[]"}
            ]
        },
        {
            "id": "trapping_rain_water",
            "title": "Trapping Rain Water",
            "difficulty": "Hard",
            "problem_statement": "Given `n` non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.",
            "examples": [
                {"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6", "explanation": "The elevation map traps 6 units of rain water."}
            ],
            "constraints": [
                "n == height.length",
                "1 <= n <= 2 * 10^4",
                "0 <= height[i] <= 10^5"
            ],
            "starter_code": {
                "Python": "def trap(height):\n    # Write your code here\n    return 0",
                "Java": "class Solution {\n    public int trap(int[] height) {\n        // Write your code here\n        return 0;\n    }\n}",
                "C++": "class Solution {\npublic:\n    int trap(vector<int>& height) {\n        // Write your code here\n        return 0;\n    }\n};",
                "JavaScript": "function trap(height) {\n    // Write your code here\n    return 0;\n}"
            },
            "hidden_test_cases": [
                {"input": "[0,1,0,2,1,0,1,3,2,1,2,1]", "expected": "6"},
                {"input": "[4,2,0,3,2,5]", "expected": "9"}
            ]
        }
    ]
}
