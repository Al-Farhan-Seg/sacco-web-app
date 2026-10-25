const form = document.querySelector("form");
const messageBox = document.getElementById("form-message");

function getInputFields() {
  const fields = form.querySelectorAll("input:not([type='submit'])");
  return fields;
}

function isEmpty(field) {
  const value = field.value;
  const trimmedValue = value.trim();
  return trimmedValue === "";
}

function getFieldName(field) {
  const selector = "label[for='" + field.id + "']";
  const label = form.querySelector(selector);
  const labelText = label.textContent;
  const nameWithoutColon = labelText.replace(":", "");
  const name = nameWithoutColon.trim();
  return name;
}

function findEmptyFields() {
  const fields = getInputFields();
  const emptyFields = [];

  for (let i = 0; i < fields.length; i++) {
    const field = fields[i];

    if (isEmpty(field)) {
      const name = getFieldName(field);
      emptyFields.push(name);
    }
  }

  return emptyFields;
}

function showError(emptyFields) {
  const fieldList = emptyFields.join(", ");
  messageBox.className = "error";
  messageBox.textContent = "Form not submitted. Please fill in: " + fieldList + ".";
}

function showSuccess() {
  messageBox.className = "success";
  messageBox.textContent = "Form submitted successfully.";
  alert("Form submitted successfully.");
}

function handleSubmit(event) {
  event.preventDefault();

  const emptyFields = findEmptyFields();

  if (emptyFields.length > 0) {
    showError(emptyFields);
    return;
  }

  showSuccess();
  form.reset();
}

form.addEventListener("submit", handleSubmit);
