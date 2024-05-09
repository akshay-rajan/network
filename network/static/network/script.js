document.addEventListener('DOMContentLoaded', () => {

    // Edit
    let editButtons = document.getElementsByClassName('edit');
    for (let i = 0; i < editButtons.length; i++) {
        let button = editButtons[i];
        button.addEventListener('click', () => editPost(button));
    }

    // Like
    let likebuttons = document.getElementsByClassName('like-button');
    for (let i = 0; i < likebuttons.length; i++) {
        let likebt = likebuttons[i];
        likebt.addEventListener('click', () => likePost(likebt));
    }
});


function editPost(button) {
    button.style.display = 'none';
    let post = button.parentNode.parentNode;
    let postID = post.querySelector('.post-id').innerText;

    // Replace the content with a textarea
    let content = post.querySelector('.post-content');
    let textarea = document.createElement('textarea');
    textarea.rows = 5;
    textarea.cols = 50;
    textarea.classList.add("form-control");
    textarea.id = "t-" + postID;
    textarea.value = content.innerHTML;
    content.replaceWith(textarea);

    // Create and enable the save button
    let save = document.createElement('button');
    save.classList.add('btn', 'btn-primary');
    save.textContent = 'Save';
    save.onclick = () => {
        savePost(postID, textarea.value);
        button.style.display = 'block';
        save.remove();
    };
    post.appendChild(save);
}


function savePost(postId, newText) {
    // Update the post on the server
    fetch(`edit/${postId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({text: newText}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Change the textarea to a div with modified text
            let content = document.createElement('div');
            content.innerHTML = newText;
            content.classList.add('post-content', 'card-body', 'my-2');
            let textarea = document.getElementById(`t-${postId}`);
            textarea.replaceWith(content);
        } else {
            console.log('Error updating post: ', data.error);
        }
    })
    .catch(error => {
        console.log(error);
    });
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function likePost(likeButton) {
    let post = likeButton.parentNode.parentNode;
    let postID = post.querySelector('.post-id').innerText;
    let likeIcon = likeButton.querySelector('.like-icon');
    let unlikeIcon = likeButton.querySelector('.unlike-icon');
    let like_display = post.querySelector('.like-count');
    const like_count = parseInt(like_display.innerText);
    let newLikeCount = 0;

    // Check whether the post is already liked, to handle UI changes
    fetch(`like_status/${postID}`)
    .then(response => {
        return response.json();
    })
    .then(data => {
        if (data.isLiked) {
            likeIcon.style.display = 'block';
            unlikeIcon.style.display = 'none';
            newLikeCount = like_count - 1;
        } else {
            likeIcon.style.display = 'none';
            unlikeIcon.style.display = 'block';
            newLikeCount = like_count + 1;
        }
        like_display.textContent = newLikeCount;
    })

    // Like/Unlike
    fetch(`like/${postID}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
}

function liked(button){
    button.classList.toggle("liked");
}
