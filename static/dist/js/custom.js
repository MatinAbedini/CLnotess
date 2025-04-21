function filterHomeworks(lessons) {
    // Get selected statuses and save them inside a list
    // Get selected lessons and save them inside a list

    const selected_statuses = [
        $("#done").prop("checked") ? 1: "",
        $("#in_progress").prop("checked") ? 2: "",
        $("#not_done").prop("checked") ? 3: "",
    ].filter(Boolean);

    const selected_lessons = lessons
        .map(lesson => $(`#${lesson}`).prop("checked") ? lesson: "")
        .filter(Boolean);

    // Set statuses and lessons which are going to get filtered,
    // And save them in form fields
    // And submit the form

    $("#status").val(selected_statuses.join(","));
    $("#lesson").val(selected_lessons.join(","));
    $("#filter_form").submit();
}

function filterExams(lessons) {
    // Get selected statuses and save them inside a list
    // Get selected difficulties and save them inside a list
    // Get selected lessons and save them inside a list

    const selected_statuses = [
        $("#done").prop("checked") ? 1: "",
        $("#not_done").prop("checked") ? 2: "",
    ].filter(Boolean);

    const selected_difficulties= [
        $("#easy").prop("checked") ? 1: "",
        $("#average").prop("checked") ? 2: "",
        $("#hard").prop("checked") ? 3: "",
    ].filter(Boolean);

    const selected_lessons = lessons
        .map(lesson => $(`#${lesson}`).prop("checked") ? lesson: "")
        .filter(Boolean);

    // Set statuses, difficulties and lessons, which are going to get filtered,
    // And save them in form fields
    // And submit the form

    $("#difficulty").val(selected_difficulties.join(","));
    $("#status").val(selected_statuses.join(","));
    $("#lesson").val(selected_lessons.join(","));
    $("#filter_form").submit();
}

function filterInvitations(lessons) {
    // Get selected statuses and save them inside a list
    // Get selected types and save them inside a list
    // Gets Select lessons and save them inside a list

    const selected_statuses = [
        $("#done").prop("checked") ? 1: "",
        $("#in_progress").prop("checked") ? 2: "",
        $("#not_done").prop("checked") ? 3: "",
    ].filter(Boolean).join(",");

    const selected_types= [
        $("#student").prop("checked") ? 1: "",
        $("#teacher").prop("checked") ? 2: "",
    ].filter(Boolean).join(",");

    const selected_lessons = lessons
        .map(lesson => $(`#${lesson}`).prop("checked") ? lesson: "")
        .filter(Boolean)
        .join(",");

    // Set statuses, types and lessons, which are going to get filtered,
    // And save them in form fields
    // And submit the form

    $("#status").val(selected_statuses);
    $("#lesson").val(selected_lessons);
    $("#type").val(selected_types);
    $("#filter_form").submit();
}

function fillPage(page) {
    $("#page").val(page);
    $("#filter_form").submit();
}
