// Widget de estrellas: la única pieza interactiva del sitio (ADR-006).
// Llama a la API JSON con la cookie de sesión y recarga para reflejar
// el nuevo promedio.

document.querySelectorAll(".calificar").forEach(function (bloque) {
  var idPelicula = bloque.dataset.pelicula;
  var botones = Array.prototype.slice.call(bloque.querySelectorAll(".estrella"));

  botones.forEach(function (boton) {
    boton.addEventListener("click", function () {
      var estrellas = Number(boton.dataset.valor);
      fetch("/api/calificaciones", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin", // envía la cookie de sesión
        body: JSON.stringify({ pelicula_id: Number(idPelicula), estrellas: estrellas })
      })
        .then(function (respuesta) {
          if (respuesta.ok) {
            window.location.reload();
          } else {
            alert("No se pudo guardar la calificación (¿se venció tu sesión?).");
          }
        })
        .catch(function () {
          alert("Error de conexión al calificar.");
        });
    });

    // Vista previa al pasar el mouse: se iluminan las estrellas hasta el cursor
    boton.addEventListener("mouseenter", function () {
      var valor = Number(boton.dataset.valor);
      botones.forEach(function (b) {
        b.classList.toggle("brillo", Number(b.dataset.valor) <= valor);
      });
    });
  });

  bloque.querySelector(".selector").addEventListener("mouseleave", function () {
    botones.forEach(function (b) { b.classList.remove("brillo"); });
  });
});