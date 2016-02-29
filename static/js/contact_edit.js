$(document).ready(function() {
    var itemFieldNumber = 0;
    var twitterFieldTemplate = Handlebars.compile($('#js-blank-twitter-field').html());
    var emailFieldTemplate = Handlebars.compile($('#js-blank-email-field').html());
    var URLFieldTemplate = Handlebars.compile($('#js-blank-url-field').html());
    var phoneFieldTemplate = Handlebars.compile($('#js-blank-phone-field').html());
    var textFieldTemplate = Handlebars.compile($('#js-blank-text-field').html());
    var dateFieldTemplate = Handlebars.compile($('#js-blank-date-field').html());
    var addressFieldTemplate = Handlebars.compile($('#js-blank-address-field').html());
    $('.js-add-email').on('click', function() {
        $('#js-email-fields').append(
            emailFieldTemplate({newItemNumber: itemFieldNumber.toString()})
        ).on('click', '.js-remove-field', function() {
            $('#' + $(this).attr('field_id')).remove();
        });
        $(this).blur();
        itemFieldNumber++;
    });
    $('.js-add-twitter').on('click', function() {
        $('#js-twitter-fields').append(
            twitterFieldTemplate({newItemNumber: itemFieldNumber.toString()})
        ).on('click', '.js-remove-field', function() {
            $('#' + $(this).attr('field_id')).remove();
        });
        $(this).blur();
        itemFieldNumber++;
    });
    $('.js-add-url').on('click', function() {
        $('#js-url-fields').append(
            URLFieldTemplate({newItemNumber: itemFieldNumber.toString()})
        ).on('click', '.js-remove-field', function() {
            $('#' + $(this).attr('field_id')).remove();
        });
        $(this).blur();
        itemFieldNumber++;
    });
    $('.js-add-phone').on('click', function() {
        $('#js-phone-fields').append(
            phoneFieldTemplate({newItemNumber: itemFieldNumber.toString()})
        ).on('click', '.js-remove-field', function() {
            $('#' + $(this).attr('field_id')).remove();
        });
        $(this).blur();
        itemFieldNumber++;
    });
    $('.js-add-text').on('click', function() {
        $('#js-text-fields').append(
            textFieldTemplate({newItemNumber: itemFieldNumber.toString()})
        ).on('click', '.js-remove-field', function() {
            $('#' + $(this).attr('field_id')).remove();
        });
        $(this).blur();
        itemFieldNumber++;
    });
    $('.js-add-date').on('click', function() {
        $('#js-date-fields').append(
            dateFieldTemplate({newItemNumber: itemFieldNumber.toString()})
        ).on('click', '.js-remove-field', function() {
            $('#' + $(this).attr('field_id')).remove();
        });
        $(this).blur();
        itemFieldNumber++;
    });
    $('.js-add-address').on('click', function() {
        $('#js-address-fields').append(
            addressFieldTemplate({newItemNumber: itemFieldNumber.toString()})
        ).on('click', '.js-remove-field', function() {
            $('#' + $(this).attr('field_id')).remove();
        });
        $(this).blur();
        itemFieldNumber++;
    });
    $('.js-remove-field').on('click', function(){
        if ($(this).attr('field_id').indexOf('new') < 0) {
            var deleted = $('#deleted_fields').val();
            deleted = deleted + $(this).attr('field_id') + ',';
            $('#deleted_fields').val(deleted);
        }
        $('#' + $(this).attr('field_id')).remove();
    });
});