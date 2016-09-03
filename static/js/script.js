$(document).ready(function () {
    $("#product_form").addClass('hidden');
    $("#add_product").addClass('visible');
    $("#add_product").click(slideToggleForm);
    $("#cancel_product").click(slideToggleForm);
    $("#submit_product").click(addProduct);

});



function slideToggleForm() {
    $("#product_form").slideToggle().removeClass();
    $("#add_product").slideToggle().removeClass();
}

function addProduct(e) {
    e.preventDefault();
    var review = {
        title: $("#id_title").val(),
        content: $("#id_content").val(),
        rating: $("#id_rating").val(),
        slug: $("#id_slug").val(),
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value
    };

    url = "/product/add/";


    $.ajax({
        url: url,
        type: "POST",
        data: review,
        //data: {csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value},
        dataType: "json",
        success: function (response) {
            $("#review_errors").empty();
            if (response.success == "True") {
                $("#submit_product").attr('disabled', 'disabled');
                $("#no_reviews").empty();
                $("#reviews").prepend(response.html).slideDown();
                new_review = $("#reviews").children(":first");
                new_review.addClass('new_review');
                $("#product_form").slideToggle();
            }
            else {
                $("#review_errors").append(response.html);
            }
        }
    });
}

