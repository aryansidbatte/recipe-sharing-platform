"use strict";

// small helper
function ajax(url, method, data, cb) {
  const opt = {
    method,
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
  };
  if (data) opt.body = JSON.stringify(data);

  return fetch(url, opt)
    .then((r) => r.json())
    .then((j) => {
      if (j.errors?.length) {
        alert("Validation error:\n" + JSON.stringify(j.errors));
      } else if (cb) cb(j);
    })
    .catch(() => alert("Network error"));
}

// vue config
const app = {
  data() {
    return {
      // db tables
      recipes: [],
      filtered_recipes: [],
      ingredients: [],
      selected_ingredients: [],

      // search boxes
      ingredient_search: "",

      // modal & form 
      showModal: false,
      newRecipe: {
        name: "",
        type: "",
        description: "",
        instruction_steps: "",
        servings: 1,
        selected: [],        // [ingredient id, …]
        qty: {},             // {id: quantity_per_serving}
        imageFile: null,
      },
    };
  },

  computed: {
    /* live calorie preview inside the modal */
    calculatedCalories() {
      if (this.newRecipe.selected.length === 0) return null;
      let perServing = 0;
      this.newRecipe.selected.forEach((id) => {
        const ing = this.ingredients.find((x) => x.id === id);
        if (ing) {
          const q = this.newRecipe.qty[id] || 1;
          perServing += q * ing.calories_per_unit;
        }
      });
      return perServing * (this.newRecipe.servings || 1);
    },
  },

  methods: {
    // search boxes
    search() {
      const t = this.ingredient_search.toLowerCase().trim();
      this.selected_ingredients = this.ingredients.filter((i) =>
        i.name.toLowerCase().includes(t)
      );
    },
    search_recipes(txt) {
      const t = (txt || "").toLowerCase();
      this.filtered_recipes = this.recipes.filter(
        (r) => r.name.toLowerCase().includes(t) || r.type.toLowerCase().includes(t)
      );
    },
    onFileChange(evt) {
      this.newRecipe.imageFile = evt.target.files[0] || null;
    },

    // modal controls
    openModal() {
      this.resetForm();
      this.showModal = true;
    },
    closeModal() {
      this.showModal = false;
    },
    resetForm() {
      this.newRecipe = {
        name: "",
        type: "",
        description: "",
        instruction_steps: "",
        servings: 1,
        selected: [],
        qty: {},
      };
    },

    // CRUD calls
    saveRecipe() {
    if (!this.newRecipe.name || !this.newRecipe.type ||
        this.newRecipe.selected.length === 0) {
        alert("Fill required fields and pick at least one ingredient.");
        return;
    }

    /* -------- build multipart/form-data -------- */
    const fd = new FormData();
    fd.append("name",         this.newRecipe.name);
    fd.append("type",         this.newRecipe.type);
    fd.append("description",  this.newRecipe.description);
    fd.append("instruction_steps", this.newRecipe.instruction_steps);
    fd.append("servings",     this.newRecipe.servings);

    // ingredients list as JSON string
    fd.append("ingredients",
                JSON.stringify(
                this.newRecipe.selected.map(id => ({
                    id,
                    qty: this.newRecipe.qty[id] || 1,
                }))
                ));

    if (this.newRecipe.imageFile) {
        fd.append("image", this.newRecipe.imageFile);
    }

    /* -------- POST -------- */
    fetch("/recipe/api/recipe", {
        method: "POST",
        body: fd,
        credentials: "same-origin",
    })
    .then(r => r.json())
    .then(res => {
        alert("Recipe saved! Total calories = " + res.total_calories);
        this.closeModal();
        this.loadRecipes();
    })
    .catch(() => alert("Network error"));
    },

    // load data
    loadRecipes() {
      ajax("/recipe/api/recipes", "GET", null, (res) => {
        this.recipes = res.recipes;
        this.filtered_recipes = res.recipes;
      });
    },
    loadIngredients() {
      ajax("/recipe/api/ingredients", "GET", null, (res) => {
        this.ingredients = res.ingredients;
        this.selected_ingredients = res.ingredients;
      });
    },
  },

  /* ---------------------------------------------------------------- */
  /* life-cycle                                                       */
  /* ---------------------------------------------------------------- */
  mounted() {
    this.loadRecipes();
    this.loadIngredients();
  },
};

/* mount */
Vue.createApp(app).mount("#app");