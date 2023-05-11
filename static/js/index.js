$(function () {
  $("[id*=getOneRecipe]").each(function (index, item) {
    item.addEventListener("click", function () {
      let recipeId = $(this).attr("data-rid");
      $.ajax({
        type: "GET",
        url: "/recipes/one/",
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

  $("[id*=getAllRecipes]").each(function (index, item) {
    item.addEventListener("click", function () {
      $.ajax({
        type: "GET",
        url: "/recipes/all/",
        success: function (data) {
          console.log("success");
        },
        error: function (err) {
          console.log("error here");
        },
      });
    });
  });
});
