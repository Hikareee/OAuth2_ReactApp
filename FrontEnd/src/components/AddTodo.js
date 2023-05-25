import Modal from "./Modal";
import { useState } from "react";
import "../styles/addTodo.css";
import { db } from "../firebase";
import { collection, addDoc, Timestamp } from "firebase/firestore";
import axios from "axios"; // add this one before you could use axios to consume the api endpoint

function AddTodo({ onClose, open }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [number, setNumber] = useState(0);

  //this request is to get the id from the server and update the number
  axios
    .get("http://localhost:8000/")
    .then((response) => {
      setNumber(Object.values(response.data)[0] + 1); // add 1 to the last id for new id
    })
    .catch(function (error) {
      console.log(error);
    });

  /* function to add new task to firestore */
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await addDoc(collection(db, "todo1"), {
        title: title,
        description: description,
        completed: false,
        created: Timestamp.now(),
      });
      onClose();
    } catch (err) {
      alert(err);
    }
  };

  /* function to add new task to BackEnd API */
  const handleSubmitAPI = async (e) => {
    e.preventDefault();
    try {
      await axios
        .post("http://localhost:8000/createTodo", {
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
    <Modal modalLable="Add Todo" onClose={onClose} open={open}>
      <form onSubmit={handleSubmitAPI} className="addTodo" name="addTodo">
        <input
          type="string"
          name="title"
          onChange={(e) => setTitle(e.target.value.toUpperCase())}
          value={title}
          placeholder="Enter title"
        />
        <textarea
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Enter task decription"
          value={description}
        ></textarea>
        <button type="submit">Done</button>
      </form>
    </Modal>
  );
}

export default AddTodo;
