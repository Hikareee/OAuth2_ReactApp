import Modal from "./Modal";
import { useState } from "react";
import "../styles/editTodo.css";
import { doc, updateDoc } from "firebase/firestore";
import { db } from "../firebase";
import axios from "axios"

function EditTodo({ open, onClose, toEditTitle, toEditDescription, id }) {
  const [title, setTitle] = useState(toEditTitle);
  const [description, setDescription] = useState(toEditDescription);
  const [number, setNumber] = useState(0);
   axios
    .get("http://localhost:8000/")
    .then((response) => {
      setNumber(Object.values(response.data)[0] + 1); // add 1 to the last id for new id
    })
    .catch(function (error) {
      console.log(error);
    });

  /* function to update document in firestore */
  const handleUpdate = async (e) => {
    e.preventDefault();
    const taskDocRef = doc(db, "todo1", id);
    try {
      await updateDoc(taskDocRef, {
        title: title,
        description: description,
      });
      onClose();
    } catch (err) {
      alert(err);
    }
  };
   const handleSubmitAPI = async (e) => {
    e.preventDefault();
    try {
      await axios
        .put("http://localhost:8000/" + number, {
          title: title,
          description: description,
          completed: false,
          created: "Timestamp.now()",
        })
        .then(function (response) {
          console.log(response.status);
          window.location.reload();
        })
        .catch(function (error) {
          console.log(error);
        });
      onClose();
    } catch (err) {
      alert(err);
    }
  };

  return (
    <Modal modalLable="Edit Todo" onClose={onClose} open={open}>
      <form onSubmit={handleUpdate} className="editTodo" name="updateTodo">
        <input
          type="text"
          name="title"
          onChange={(e) => setTitle(e.target.value.toUpperCase())}
          value={title}
        />
        <textarea
          onChange={(e) => setDescription(e.target.value)}
          value={description}
        ></textarea>
        <button type="submit">Edit</button>
      </form>
    </Modal>
  );
}

export default EditTodo;
