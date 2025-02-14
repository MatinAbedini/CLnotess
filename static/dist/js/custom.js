function filterHomeworks(lessons) {
    // Get selected statuses and save them inside a list
    // Gets Select lessons and save them inside a list

    const selected_statuses = [
        $("#done").prop("checked") ? 1: "",
        $("#in_progress").prop("checked") ? 2: "",
        $("#not_done").prop("checked") ? 3: "",
    ].filter(Boolean).join(",");

    const selected_lessons = lessons
        .map(lesson => $(`#${lesson}`).prop("checked") ? lesson: "")
        .filter(Boolean)
        .join(",");

    // Set statuses and lessons which are going to get filtered,
    // And save them in form fields
    // And submit the form

    $("#status").val(selected_statuses);
    $("#lesson").val(selected_lessons);
    $("#filter_form").submit();
}

function filterExams(lessons) {
    // Get selected statuses and save them inside a list
    // Get selected difficulties and save them inside a list
    // Gets Select lessons and save them inside a list

    const selected_statuses = [
        $("#done").prop("checked") ? 1: "",
        $("#in_progress").prop("checked") ? 2: "",
        $("#not_done").prop("checked") ? 3: "",
    ].filter(Boolean).join(",");

    const selected_difficulties= [
        $("#easy").prop("checked") ? 1: "",
        $("#average").prop("checked") ? 2: "",
        $("#hard").prop("checked") ? 3: "",
    ].filter(Boolean).join(",");

    const selected_lessons = lessons
        .map(lesson => $(`#${lesson}`).prop("checked") ? lesson: "")
        .filter(Boolean)
        .join(",");

    // Set statuses, difficulties and lessons, which are going to get filtered,
    // And save them in form fields
    // And submit the form

    $("#status").val(selected_statuses);
    $("#difficulty").val(selected_difficulties);
    $("#lesson").val(selected_lessons);
    $("#filter_form").submit();
}

function fillPage(page) {
    debugger;
    $("#page").val(page);
    $("#filter_form").submit();
}
