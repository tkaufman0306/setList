// setlist.js file to enable reordering and removing songs in a setlist

// static/js/setlist.js

document.getElementById("edit-button").addEventListener("click", function () {
  document.querySelectorAll(".remove-button").forEach((button) => {
    button.computedStyleMap.display =
      button.style.display === "none" ? "inline" : "none";
  });
  this.textContent = this.textContent === "Edit" ? "Done" : "Edit";
});

document.querySelectorAll(".remove-button").forEach((button) => {
  button.addEventListener("click", function () {
    const li = this.parentElement;
    const songId = li.getAttribute("data-song-id");
    li.remove();

    fetch(`/setlist/${setlistId}/remove-song`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ song_id: songId }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          console.log("Song removed successfully.");
        } else {
          console.error("Failed to remove song.");
        }
      });
  });
});

document
  .getElementById("song-list")
  .addEventListener("dragstart", function (e) {
    if (e.target.tagName === "LI") {
      e.dataTransfer.setData(
        "text/plain",
        e.target.getAttribute("data-song-id")
      );
    }
  });

document.getElementById("song-list").addEventListener("dragover", function (e) {
  e.preventDefault();
  const afterElement = getDragAfterElement(e.target, e.clientY);
  const draggable = document.querySelector(".dragging");
  if (afterElement == null) {
    e.target.appendChild(draggable);
  } else {
    e.target.insertBefore(draggable, afterElement);
  }
});

function getDragAfterElement(container, y) {
  const draggableElements = [
    ...container.querySelectorAll("li:not(.dragging)"),
  ];
  return draggableElements.reduce(
    (closest, child) => {
      const box = child.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child };
      } else {
        return closest;
      }
    },
    { offset: Number.NEGATIVE_INFINITY }
  ).element;
}
