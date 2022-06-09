import React, { useState, useEffect } from "react";
import banner from "./images/banner4.jpg"
import SearchIcon from '@mui/icons-material/Search';
import Search from "./search";
import kdrama from "./kdrama.json"

function Home () {

    const [recs, setRecs] = useState([]);
    const [recsCast, setRecsCast] = useState([]);
    const [recentlyFinished, setRecentlyFinished] = useState([]);
    const [trending, setTrending] = useState([]);

    useEffect( () => {
        fetch("/recently-finished")
        .then(res => res.json())
        .then(resjson => {
            setRecentlyFinished(resjson["dramas"])
        });
    }, [])

    useEffect( () => {
        fetch("/trending")
        .then(res => res.json())
        .then(resjson => {
            setTrending(resjson["dramas"])
        });
    }, [])

    const createBox = (drama, side) => {

        const redirect = () => {
            window.open("https://www.google.com/search?q=" + drama[0].replace(" ", "+"), '_blank');
        };

        return (
            <div className={drama[2] >= 9 ? "recommendations-box-gold": "recommendations-box"} onClick={e => redirect()} style={{ marginTop: side ? "1em" : "0em"}}>
                <img src={drama[1]} className="recommendations-image"/>
                <div className="recommendations-title">
                    {drama[0]}
                </div>
                <div className="recommendations-star">
                    <i class="fa fa-star" style={{color: "yellow"}} ria-hidden="true"></i> {drama[2]}
                </div>
            </div>            
        )
    }

    return (
        <div>
            <div className="hero-container">
                <img src={banner} className="hero-image"/>
            </div>
            <div className="slogan">
                Welcome to DramaNext!
            </div>
            <div className="body-container">
                <div className="bar">
                    <div className="bar-description">
                    RECENTLY COMPLETED
                    </div>
                    {
                        recentlyFinished.map( (drama) => {
                            return createBox(drama, true)
                        })
                    }
                </div>
                <div className="recommendations-container">
                    <div className="search-description">
                        <span style={{color: "rgb(55, 53, 47)"}}>&#9654;</span>&nbsp; CHOOSE A KDRAMA YOU LIKE AND WE'LL RECOMMEND SOME MORE SIMILAR
                    </div>
                    <Search data={kdrama} func={[setRecs, setRecsCast]}/>
                    <div className="recommendations-description">
                        <i class="fa fa-list" style={{color: "rgb(55, 53, 47)"}} ria-hidden="true"></i>&nbsp; RECOMMENDATIONS
                    </div>
                    {recs.length !=0 && (
                        <div className="recommendations-header">
                            TOP RECOMMENDATIONS
                        </div>
                    )}
                    <div className="recommendations-row">
                    {
                            recs.slice(0,5).map( (drama) => {
                                return createBox(drama, false)
                            })
                    }
                    </div>
                    {recsCast.length !=0 && (
                        <div className="recommendations-header">
                            WATCH IF YOU LIKED THE CAST
                        </div>
                    )}
                    <div className="recommendations-row">
                    {
                            recsCast.slice(0,5).map( (drama) => {
                                return createBox(drama, false)
                            })
                    }
                    </div>
                </div>
                <div className="bar">
                    <div className="bar-description">
                    TRENDING DRAMAS
                    </div>
                    {
                        trending.map( (drama) => {
                            return createBox(drama, true)
                        })
                    }
                </div>
            </div>
        </div>
    )
}

export default Home;
  