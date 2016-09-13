$(document).ready(function () {
    $("#product_form").css('display', 'none');
    $("#add_product").css('display', 'block');
    $("#add_product").click(slideToggleForm);
    $("#submit_product").click(addProduct);
    $("#product_list").on('click', '.submit_add_to_order', addToOrder);
    $("#order_items_delivery").on('click', '.add_to_delivery_btn', addToDelivery);
    $("#order_items_list").on('click', '.delete_from_order_btn', deleteFromOrder);
    $("#get_orderitems_btn").click(extractOrderItems);
    // $(".submit_add_to_order").click(addToOrder);
});


function addToDelivery(e) {
    e.preventDefault();
    console.log('Click!');
    var oi_id = $(this).attr('id');
    var delivery_num = $('span#delivery_num').text();
    console.log(oi_id, delivery_num);


    var data = {
        oi_id: oi_id,
        delivery_num: delivery_num
    };

    url = "/orderitem_to_delivery";

    $.ajax({
        url: url,
        type: "GET",
        data: data,
        dataType: "json",
        success: function (response) {
            $(".product_errors").empty();
            console.log(response.html);
            if (response.success == "True") {
                $("#order_items_list").append(response.html).slideDown();
            }
            else {
                $(".product_errors").append(response.html);
            }
        }
    });
}


function extractOrderItems(e) {
    e.preventDefault();
    var data = {
        order_num: $('#order_num').val()
    };
    url = "/get_orderitems";
    $.ajax({
        url: url,
        type: "GET",
        data: data,
        dataType: "json",
        success: function (response) {
            $("#order_items_delivery").html(response.html);
        }
    });
}

function slideToggleForm() {
    $("#product_form").slideToggle();
    $("#add_product").slideToggle();
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
    console.log(data);

    url = "/product_create";

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
                $("#add_product").slideToggle();
                $("#id_name").val('');
                $("#id_categories").val('');
                $("#id_description").val('');
            }
            else {
                $(".product_errors").append(response.html);
                console.log(response.html)
            }
        }
    });
}

function addToOrder(e) {
    e.preventDefault();

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

    console.log(data);

    url = "/product_to_order";

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


function deleteFromOrder(e) {
    e.preventDefault();
    var row = $(this).parents('tr');
    var oi_id = $(this).attr('id');
    console.log(oi_id);

    var data = {
        oi_id: oi_id
    };

    url = "/delete_oi_from_order";

    $.ajax({
        url: url,
        type: "GET",
        data: data,
        dataType: "json",
        success: function (response) {
            console.log(response.html);
            row.remove();
        }
    });
}


$('.datepicker').datepicker({
    todayBtn: "linked",
    language: "ru",
    daysOfWeekHighlighted: "0,6",
    todayHighlight: true,
    orientation: 'bottom',
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