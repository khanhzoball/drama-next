import React, { useState, useEffect } from "react";
import banner1 from "./images/banner1.jpg"
import SearchIcon from '@mui/icons-material/Search';
import Search from "./search";
import kdrama from "./kdrama.json"

function Home () {

    const [recs, setRecs] = useState([]);

    const createBox = (drama) => {

        const redirect = () => {
            console.log(2);
            window.location.href = drama[3];
        };

        return (
            <a className="recommendations-box" href={
                drama[3].slice(0, 8) + "www." + drama[3].slice(8, drama[3].length)
            } target="_blank">
                <img src={drama[1]} className="recommendations-image"/>
                <div className="recommendations-title">
                    {drama[0]}
                </div>
                <div className="recommendations-star">
                    <i class="fa fa-star" style={{color: "yellow"}} ria-hidden="true"></i> {drama[2]}
                </div>
            </a>            
        )
    }

    return (
        <div>
            <div className="hero-container">
                <img src={banner1} className="hero-image"/>
            </div>
            <div className="slogan">
                Welcome to DramaNext!
            </div>
            <div className="search-description">
                <span style={{color: "rgb(55, 53, 47)"}}>&#9654;</span>&nbsp; CHOOSE A KDRAMA YOU LIKE AND WE'LL RECOMMEND SOME MORE SIMILAR
            </div>
            <Search data={kdrama} func={setRecs}/>
            <div className="recommendations-container">
                <div className="recommendations-description">
                    <i class="fa fa-list" style={{color: "rgb(55, 53, 47)"}} ria-hidden="true"></i>&nbsp; RECOMMENDATIONS
                </div>
                <div className="recommendations-header">
                    TOP RECOMMENDATIONS
                </div>
                <div className="recommendations-row">
                {
                        recs.slice(0,5).map( (drama) => {
                            return createBox(drama)
                        })
                }
                </div>
            </div>
        </div>
    )
}

export default Home;
  