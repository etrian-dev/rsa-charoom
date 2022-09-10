function edit_msg(event) {
    var formData = {
      msg: $("#message").val(),
    };

    $.ajax({
      type: "PUT",
      url: this.action,
      data: JSON.stringify(formData),
      contentType: "application/json",
      dataType: "json",
      encode: true,
    }).done(function (data) {
        window.location.href = data['url']
        //alert("Message updated successfully");
    }).fail(function(data) {
        //alert("Failed message update");
    }).always(function(data) {
        console.log("msg-edit: ", JSON.stringify(data));
    });

    event.preventDefault();
}

function delete_msg(event) {
    $.ajax({
      type: "DELETE",
      url: this.href,
      contentType: "application/json",
      dataType: "json",
      encode: true,
    }).done(function (data) {
        window.location.href = data['url']
        alert("Message deleted successfully");
    }).fail(function(data) {
        alert("Failed message deletion");
    }).always(function(data) {
        console.log("msg-delete");
    });

    event.preventDefault();
}

function search_user(event) {
    var url = document.URL;

    $.ajax({
        type: "GET",
        url: "/search/",
        data: { "user": $("#query").val()},
        contentType: "application/json",
        dataType: "json",
        encode: true,
        success: function(data) {
            // process the json data
            matching_users = data
            select_node = document.getElementById("matching-users");
            while (select_node.firstChild) {
                select_node.removeChild(select_node.lastChild);
            }
            for (const user of matching_users) {
                var opt = document.createElement('option');
                opt.value = user.user_id
                opt.innerHTML = user.username + " (user_id: " + user.user_id + ")";
                select_node.appendChild(opt);
            }
            select_node.firstChild.selected = true;
            console.log("user-search: " + query);
        }
    }).fail(function(data) {
        alert("Failed query");
    }).always(function(data) {
        console.log("user-search", data);
    });

    event.preventDefault();
}

$(document).ready(function () {
  $("#msg-edit-form").on("submit", edit_msg);
  $("#msg-delete").on("click", delete_msg);
  $("#user-search").on("change", search_user);
  $("#user-search").on("submit", search_user);
});

