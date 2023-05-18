import React, { Component } from 'react';
import Modal from 'react-modal';
import "./ButtonModal.css";

class ButtonModal extends Component {
  state = {
    showModal: false
  };

  handleOpenModal = () => {
    this.setState({ showModal: true });
  };

  handleCloseModal = () => {
    this.setState({ showModal: false });
  };

  render() {
    const { buttonText, handleMinChange, handleMaxChange } = this.props;
    const { showModal } = this.state;

    const modalStyle = {
        content: {
          position: 'absolute',
          top: '40px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#fff',
          border: '1px solid #ccc',
          padding: '20px',
          zIndex: '9999',
          width: '200px',
          height: '100px',
          boxShadow: '0 0 10px rgba(0, 0, 0, 0.3)'
        },
        overlay: {
          backdropFilter: 'blur(3px)',
          background: 'rgba(0,0,0,0.5)',
          position: 'fixed',
          left: '0',
          top: '0',
          right: '0',
          bottom: '0'
        }
      };
  

    return (
      <div>
        <button onClick={this.handleOpenModal} class="button">{buttonText}</button>
        <Modal isOpen={showModal} onRequestClose={this.handleCloseModal} style={modalStyle}>
            <div>
                <label>{buttonText}</label><br></br>
                <input class="input-number" type="text" placeholder="От" onChange={handleMinChange}></input>
                <input class="input-number" type="text" placeholder="До" onChange={handleMaxChange}></input>
                <button onClick={this.handleCloseModal} class="button">Применить</button>
            </div>
        </Modal>
      </div>
    );
  }
}

export default ButtonModal;
