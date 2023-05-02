$(function () {
  $("[id*=getRecipe]").each(function (index, item) {
    item.addEventListener("click", function () {
      let recipeId = $(this).attr("data-rid");
      $.ajax({
        type: "GET",
        url: "/run/",
        data: { id: recipeId },
        success: function (data) {
          // $("#id_city").html(data);
          console.log("success");
        },
        error: function (err) {
          console.log("error here");
        },
      });
    });
  });
});
