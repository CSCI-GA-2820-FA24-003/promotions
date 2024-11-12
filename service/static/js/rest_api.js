$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#promotion_id").val(res.id);
        $("#promotion_title").val(res.title);
        $("#promotion_description").val(res.description);
        $("#promotion_promo_code").val(res.promo_code);
        $("#promotion_promo_value").val(res.promo_value);
        $("#promotion_promo_type").val(res.promo_type);
        $("#promotion_start_date").val((new Date(res.start_date)).toISOString().split('T')[0]);
        $("#promotion_created_date").val((new Date(res.created_date)).toISOString().split('T')[0]);
        $("#promotion_duration").val(res.duration);
        if (res.active == true) {
            $("#promotion_active").val("true");
        } else {
            $("#promotion_active").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#promotion_id").val("");
        $("#promotion_title").val("");
        $("#promotion_description").val("");
        $("#promotion_promo_code").val("");
        $("#promotion_promo_value").val("");
        $("#promotion_promo_type").val("");
        $("#promotion_start_date").val("");
        $("#promotion_created_date").val("");
        $("#promotion_duration").val("");
        $("#promotion_active").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Promotion
    // ****************************************

    $("#create-btn").click(function () {
        let title = $("#promotion_title").val();
        let description = $("#promotion_description").val();
        let promo_code = $("#promotion_promo_code").val();
        let promo_value = $("#promotion_promo_value").val();
        let promo_type = $("#promotion_promo_type").val();
        let start_date = $("#promotion_start_date").val();
        let created_date = $("#promotion_created_date").val();
        let duration = $("#promotion_duration").val();
        let active = $("#promotion_active").val() === 'true';

        if(promo_type === ""){
            if(promo_type === ""){
                flash_message("Promotion type cannot be empty")
                return;
            }
        }

        let data = {
            "title": title,
            "description": description,
            "promo_code": promo_code,
            "promo_type": promo_type,
            "promo_value": promo_value,
            "start_date": start_date,
            "created_date": created_date,
            "duration": duration,
            "active": active,
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/promotions",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Promotion
    // ****************************************

    $("#update-btn").click(function () {
        let promotion_id = $("#promotion_id").val();

        let title = $("#promotion_title").val();
        let description = $("#promotion_description").val();
        let promo_code = $("#promotion_promo_code").val();
        let promo_value = $("#promotion_promo_value").val();
        let promo_type = $("#promotion_promo_type").val();
        let start_date = $("#promotion_start_date").val();
        let created_date = $("#promotion_created_date").val();
        let duration = $("#promotion_duration").val();
        let active = $("#promotion_active").val() === 'true';

        if(promo_type === ""){
            flash_message("Promotion type cannot be empty")
            return;
        }

        let data = {
            "title": title,
            "description": description,
            "promo_code": promo_code,
            "promo_type": promo_type,
            "promo_value": promo_value,
            "start_date": start_date,
            "created_date": created_date,
            "duration": duration,
            "active": active,
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/promotions/${promotion_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Promotion
    // ****************************************

    $("#retrieve-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete a Promotion
    // ****************************************

    $("#delete-btn").click(function () {

        let promotion_id = $("#promotion_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/promotions/${promotion_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Promotion has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#promotion_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for a Promotion
    // ****************************************

    $("#search-btn").click(function () {
        let fields = [
            'title',
            'description',
            'promo_code',
            'promo_type',
            'promo_value',
            'start_date',
            'created_date',
            'duration',
            'active',
        ]

        let queryString = ""

        for(let field of fields){
            let value = $(`#promotion_${field}`).val();
            if(value){
                if (queryString.length > 0) {
                    queryString += `&${field}=` + value
                } else {
                    queryString += `${field}=` + value
                }
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/promotions?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-1">title</th>'
            table += '<th class="col-md-2">description</th>'
            table += '<th class="col-md-1">promo_code</th>'
            table += '<th class="col-md-1">promo_value</th>'
            table += '<th class="col-md-1">duration</th>'
            table += '<th class="col-md-1">active</th>'
            table += '<th class="col-md-1">promo_type</th>'
            table += '<th class="col-md-1">start_date</th>'
            table += '<th class="col-md-1">created_date</th>'
            table += '</tr></thead><tbody>'
            let firstPromotion = "";
            for(let i = 0; i < res.length; i++) {
                let promotion = res[i];
                table +=  `<tr id="row_${i}"><td>${promotion.id}</td><td>${promotion.title}</td><td>${promotion.description}</td><td>${promotion.promo_code}</td><td>${promotion.promo_value}</td><td>${promotion.duration}</td><td>${promotion.active}</td><td>${promotion.promo_type}</td><td>${promotion.start_date}</td><td>${promotion.created_date}</td></tr>`;
                if (i == 0) {
                    firstPromotion = promotion;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstPromotion != "") {
                update_form_data(firstPromotion)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
