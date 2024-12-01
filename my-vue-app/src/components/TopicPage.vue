<template>
    <div class="topics-page">
      <h1>Let's select a topic to learn!</h1>
      <div v-for="(group, index) in groupedTopics" 
           :key="index" 
           class="topic-group">
        <h2>{{ group.heading }}</h2>
        <div class="topics-container">
          <div v-for="(topic, i) in group.topics" 
               :key="i"
               class="topic-card"
               @click="selectTopic(topic)">
            {{ topic }}
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "TopicsPage",
    data() {
      return {
        groupedTopics: [
          { heading: "Basic Data Structures", topics: ["Arrays", "Strings", "Linked Lists", "Stacks", "Queues"] },
          { heading: "Advanced Data Structures", topics: ["Trees", "Binary Search Trees", "Heaps and Priority Queues", "Tries", "Disjoint Set Union (DSU)", "Fenwick Tree (Binary Indexed Tree)", "Segment Tree", "Sparse Table"] },
          { heading: "Graph Algorithms", topics: ["Graphs", "Breadth-First Search (BFS)", "Depth-First Search (DFS)", "Shortest Path Algorithms (Dijkstra, Bellman-Ford)"] },
          { heading: "Problem-Solving Techniques", topics: ["Sliding Window", "Two Pointers", "Divide and Conquer", "Backtracking", "Greedy Algorithms", "Recursion"] },
          { heading: "Sorting and Searching", topics: ["Sorting Algorithms", "Searching Algorithms"] },
          { heading: "Mathematics and Number Theory", topics: ["Bit Manipulation", "Modular Arithmetic", "Combinatorics", "Number Theory"] },
          { heading: "Dynamic Programming (DP)", topics: ["0/1 Knapsack", "Unbounded Knapsack", "Longest Increasing Subsequence (LIS)", "Longest Common Subsequence (LCS)", "Matrix Chain Multiplication", "Coin Change", "Subset Sum", "Partition Problem", "Minimum Path Sum", "Edit Distance", "Rod Cutting", "Palindromic Substrings", "Egg Dropping Problem", "Fibonacci Variants", "Catalan Numbers", "Shortest Common Supersequence", "DP on Trees", "DP on Graphs", "State Compression DP", "Bitmasking DP", "Interval DP", "Digit DP", "Probability DP"] },
          { heading: "Game Theory and Miscellaneous", topics: ["Matrix Manipulation", "Game Theory"] },
        ],
      };
    },
    methods: {
    selectTopic(topic) {
      this.$router.push({
        name: "SampleOne",
        params: { topic: encodeURIComponent(topic) } // Encode the topic
      });
    },
  },
  };
  </script>
  
  <style scoped>
  .topics-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem;
    background-color: rgba(210, 239, 191, 0.607);
    font-family: Arial, sans-serif;
    color: white;
  }
  
  h1 {
    font-size: 2.8rem;
    margin-bottom: 1.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    color: #072e0b;
  }
  
  .topic-group {
    margin-bottom: 2rem;
    width: 100%;
    max-width: 1200px;
  }
  
  .topic-group h2 {
    font-size: 1.8rem;
    color: #315b35;
    margin-bottom: 1rem;
    text-align: left;
  }
  
  .topics-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .topic-card {
    background-color: rgba(100, 169, 101, 0.632);
    padding: 1rem;
    border-radius: 15px;
    text-align: center;
    font-size: 1.2rem;
    color: #072e0b;
    box-shadow: 0 4px 16px rgba(24, 72, 44, 0.37);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  
  .topic-card:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 24px rgba(24, 72, 44, 0.5);
  }
  </style>
  