document.getElementById("jobForm").addEventListener("submit", function (event) {
  event.preventDefault(); // Prevent form submission

  alert(
    "Thank you for filling the application!  We will get back to you after reviewing your application."
  );

  // Redirect the user back to the index.html page
  window.location.href = "index.html";
});
