$(document).ready(function () {
    $("#product_form").addClass('hidden');
    $("#add_product").addClass('visible');
    $("#add_product").click(slideToggleForm);
    $("#submit_product").click(addProduct);
    $("#product_list").on('click', '.submit_add_to_order', addToOrder);
    // $(".submit_add_to_order").click(addToOrder);

});


function slideToggleForm() {
    $("#product_form").slideToggle().removeClass();
    $("#add_product").slideToggle().removeClass();
}

function addProduct(e) {
    e.preventDefault();
    var csrf_tag = $(this).siblings('input[name=csrfmiddlewaretoken]').val();
    var data = {
        name: $("#id_name").val(),
        categories: $("#id_categories").val(),
        description: $("#id_description").val(),
        csrfmiddlewaretoken: csrf_tag
    };

    url = "/product_add";

    $.ajax({
        url: url,
        type: "POST",
        data: data,
        dataType: "json",
        success: function (response) {
            $(".product_errors").empty();
            if (response.success == "True") {
                // console.log(response.html);
                // $("#submit_product").attr('disabled', 'disabled');
                $("#product_list").append(response.html).slideDown();
                $("#product_list").children(":last").addClass('newly_added_product');
                $("#product_form").slideToggle();
                $("#add_product").slideToggle().addClass('visible');
                $("#id_name").val('');
                $("#id_categories").val('');
                $("#id_description").val('');
            }
            else {
                $(this).closest(".product_errors").append(response.html);
            }
        }
    });
}

function addToOrder(e) {
    e.preventDefault();
    console.log('Click!');
    var form_tag = $(this).closest('form');

    var order_id = $("#order_id").text();
    var product_id = form_tag.find(".product_id").val();
    var price = form_tag.find(".price").val();
    var discount = form_tag.find(".discount").val();
    var quantity = form_tag.find(".quantity").val();
    console.log(order_id, product_id, price, quantity);

    if (!price) {
        alert('Укажите цену!!!!!!!!!!!');
        return
    }

    var data = {
        order_id: order_id,
        product_id: product_id,
        price: price,
        discount: discount,
        quantity: quantity,
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value
    };

    url = "/add_to_order";

    $.ajax({
        url: url,
        type: "GET",
        data: data,
        dataType: "json",
        success: function (response) {
            $(".product_errors").empty();
            if (response.success == "True") {
                console.log(response.html);
                $("#order_items_list").append(response.html).slideDown();
            }
            else {
                alert('Ошибка!!!!!!!!!!!');
            }
        }
    });
}

$('.datepicker').datepicker({
    todayBtn: "linked",
    language: "ru",
    daysOfWeekHighlighted: "0,6",
    todayHighlight: true
});

// from my_account
$(function () {
    $('[data-toggle="popover"]').popover();
    $('[data-toggle="popover-percent"]').popover({
        html: true,
        content: function () {
            return $("#popover-2-content").html();
        },
        title: function () {
            return $("#popover-2-title").html();
        }
    })
});