import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Home from "./components/home.js";
import "./components/index.css";
import Footer from "./components/footer";

function App () {
  return (
    <div>
      <BrowserRouter>
          <Routes>
              <Route path="/" element={<Home/>}/>
          </Routes>
      </BrowserRouter>
      <Footer/>
    </div>
  )
}

export default App;