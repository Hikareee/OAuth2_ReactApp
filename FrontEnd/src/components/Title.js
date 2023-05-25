import React from "react";
import { useAuthState } from "react-firebase-hooks/auth";
import { useNavigate } from "react-router-dom";
import "../styles/title.css";
import TodoList from "./TodoList";
import AddTodo from "./AddTodo";
import { useState, useEffect } from "react";
import {
  collection,
  query,
  orderBy,
  onSnapshot,
  //getDocs,
  //where,
} from "firebase/firestore";
import { auth, db, logout } from "../firebase";
import axios from "axios"; // add this one before you could use axios to consume the api endpoint

function Title() {
  const [openAddModal, setOpenAddModal] = useState(false);
  const [task, setTask] = useState([]);
  const [user, loading, error] = useAuthState(auth);
  const [name, setName] = useState("");
  const navigate = useNavigate();
  const fetchUserName = () => {
    try {
      //const q = query(collection(db, "users"), where("uid", "==", user?.uid));
      //const doc = await getDocs(q);
      //console.log(auth._currentUser.displayName);
      //const data = doc.docs[0].data();
      //console.log(doc);
      setName(auth._currentUser.displayName);
    } catch (err) {
      console.error(err);
      console.error(error);
      //alert("Wakaka An error occured while fetching user data");
    }
  };

  /* function to get all tasks from firestore in realtime */
  const loadTodo = () => {
    const q = query(collection(db, "todos"), orderBy("created", "desc"));
    onSnapshot(q, (querySnapshot) => {
      //querySnapshot.docs.map((a) => console.log(a.data()));
      setTask(
        querySnapshot.docs.map((doc) => ({
          id: doc.id,
          data: doc.data(),
        }))
      );
    });
  };

  //function to get all tasks from Our BackEnd API in realtime
  const loadTodoAPI = () => {
    axios
      .get("http://localhost:8000/todos")
      .then((response) => {
        /*Object.keys(response.data).map((key) =>
          console.log(response.data[key])
        );*/
        setTask(
          Object.keys(response.data).map((key) => ({
            id: key,
            data: response.data[key],
          }))
        );
      })
      .catch((error) => console.error(error));
  };

  useEffect(() => {
    if (loading) return;
    if (!user) return navigate("/");
    //loadTodo(); // activate to connect with firestore
    loadTodoAPI(); //activate to cennect with our BAckend API
    fetchUserName();
  }, [user, loading]);

  /* function to get all tasks from firestore in realtime */
  //useEffect(() => {

  //}, []);

  return (
    <div className="title">
      <header>Todo App</header>
      <div className="">
        <div className="">
          Logged in as
          <div>{name}</div>
          <div>{user?.email}</div>
          <button className="dashboard__btn" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <div className="title__container">
        <button onClick={() => setOpenAddModal(true)}>New Task +</button>
        <div className="title__tasks">
          {task.map((todolist) => (
            <TodoList
              id={todolist.id}
              key={todolist.id}
              completed={todolist.data.completed}
              title={todolist.data.title}
              description={todolist.data.description}
            />
          ))}
        </div>
      </div>

      {openAddModal && (
        <AddTodo onClose={() => setOpenAddModal(false)} open={openAddModal} />
      )}
    </div>
  );
}

export default Title;
