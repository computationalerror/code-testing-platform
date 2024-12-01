<template>
    <div>
      <h1>JDoodle Embedded IDE</h1>
      <!-- JDoodle Embeddable IDE -->
      <div data-pym-src="https://www.jdoodle.com/embed/v1/a6699de47f2e7201"></div>
    </div>
  </template>
  
  <script>
  export default {
    name: "IdeHelp",
    mounted() {
      // Dynamically load the JDoodle script
      const script = document.createElement("script");
      script.src = "https://www.jdoodle.com/assets/jdoodle-pym.min.js";
      script.type = "text/javascript";
      script.onload = () => {
        console.log("JDoodle script loaded successfully.");
      };
      script.onerror = () => {
        console.error("Failed to load JDoodle script.");
      };
      document.body.appendChild(script);
    },
  };
  </script>

<style>
textarea {
  width: 100%;
  height: 150px;
  margin: 10px 0;
}
pre {
  background-color: #f8f8f8;
  padding: 10px;
  border: 1px solid #ddd;
}
</style>