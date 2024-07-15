// static/js/setlist.js




document
  .getElementById("add-song-button")
  .addEventListener("click", function() {
      const songTitle = document.getElementById("song-title").value;
      const songArtist = document.getElementById("song-artist").value;

      fetch(`/setlist/${setlistId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ title: songTitle, artist: songArtist }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            console.log("Song added successfully.");
            // Update the UI to reflect the new song
            const songList = document.getElementById("song-list");
            const newSong = document.createElement("li");
            newSong.setAttribute("data-song-id", data.song_id);
            newSong.innerHTML = `${songTitle} by ${songArtist} <button class="remove-button" style="display: none;">Remove</button>`;
            songList.appendChild(newSong);
          } else {
            console.error("Failed to add song.", data.error);
          }
        });
    });
  

  const editButton = document.getElementById("edit-button");
  if (editButton) {
    editButton.addEventListener("click", function () {
      document.querySelectorAll(".remove-button").forEach((button) => {
        button.style.display =
          button.style.display === "none" ? "inline" : "none";
      });
      this.textContent = this.textContent === "Edit" ? "Done" : "Edit";
    });
  }

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

  const songList = document.getElementById("song-list");
  if (songList) {
    songList.addEventListener("dragstart", function (e) {
      if (e.target.tagName === "LI") {
        e.dataTransfer.setData(
          "text/plain",
          e.target.getAttribute("data-song-id")
        );
      }
    });

    songList.addEventListener("dragover", function (e) {
      e.preventDefault();
      const afterElement = getDragAfterElement(e.target, e.clientY);
      const draggable = document.querySelector(".dragging");
      if (afterElement == null) {
        e.target.appendChild(draggable);
      } else {
        e.target.insertBefore(draggable, afterElement);
      }
    });
  }

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

