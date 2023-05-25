<<<<<<< HEAD
import Modal from "./Modal";
import "../styles/todo.css";

function Todo({ onClose, open, title, description }) {
  return (
    <Modal modalLable="Todo" onClose={onClose} open={open}>
      <div className="todo">
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </Modal>
  );
}

export default Todo;
=======
import Modal from "./Modal";
import "../styles/todo.css";

function Todo({ onClose, open, title, description }) {
  return (
    <Modal modalLable="Todo" onClose={onClose} open={open}>
      <div className="todo">
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    </Modal>
  );
}

export default Todo;
>>>>>>> a6fef2c88f7152d5c92ff6bde7c55fe9365def60
