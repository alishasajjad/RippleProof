"use client";

import Link from "next/link";

import {
  usePathname,
  useRouter,
} from "next/navigation";

import {
  useEffect,
  useState,
} from "react";


import {
  Activity,
  FlaskConical,
  History,
  Home,
  LogIn,
  ScanSearch,
  ShieldCheck,
  UserPlus,
} from "lucide-react";


import styles from "./SiteNavbar.module.css";



const navItems = [

  {
    label:"Home",
    href:"/",
    icon:Home,
  },


  {
    label:"Analyze",
    href:"/custom",
    icon:ScanSearch,
  },


  {
    label:"Run history",
    href:"/runs",
    icon:History,
  },


  {
    label:"Evaluation",
    href:"/evaluation",
    icon:FlaskConical,
  },

];



type User = {

  id?:string;

  name?:string;

  email?:string;

};



export default function SiteNavbar(){


const pathname = usePathname();

const router = useRouter();



const [user,setUser] =
useState<User|null>(null);


const [loading,setLoading] =
useState(true);




useEffect(()=>{


async function checkSession(){


try{


const response =
await fetch(
"/api/auth/me",
{
credentials:"include",
cache:"no-store",
}
);



if(response.ok){

const data =
await response.json();


setUser(
data.user ?? data
);


}
else{

setUser(null);

}


}

catch{

setUser(null);

}

finally{

setLoading(false);

}


}


checkSession();


},[pathname]);






async function handleLogout(){


try{

await fetch(
"/api/auth/logout",
{
method:"POST",
credentials:"include",
}
);


}

finally{


setUser(null);

router.push("/login");

router.refresh();


}


}





if(
pathname === "/login" ||
pathname === "/register"
){

return null;

}




return (

<header className={styles.header}>


<div className={styles.inner}>


<Link
href="/"
className={styles.brand}
>


<div className={styles.logo}>

<ShieldCheck size={25}/>

</div>


<div>

<div className={styles.brandName}>
RippleProof
</div>


<div className={styles.brandTagline}>
Policy Change Intelligence
</div>


</div>


</Link>





<nav className={styles.navigation}>


{
navItems.map(
(item)=>{


const Icon=item.icon;


const active =
item.href === "/"
?
pathname === "/"
:
pathname.startsWith(
item.href
);



return (

<Link
key={item.href}
href={item.href}
className={
`${styles.navItem}
${active ? styles.navItemActive:""}`
}
>


<Icon size={19}/>

<span>
{item.label}
</span>


</Link>

);


}

)

}


</nav>





<div className={styles.actions}>


{
loading ? null :

user ? (

<>


<Link
href="/custom"
className={styles.productionBadge}
>

<Activity size={17}/>

<span>
Production console
</span>

</Link>



<button
className={styles.signInButton}
onClick={handleLogout}
>

Sign out

</button>


</>


)

:

(

<>


<Link
href="/login"
className={styles.signInButton}
>

<LogIn size={17}/>

<span>
Sign in
</span>

</Link>




<Link
href="/register"
className={styles.getStartedButton}
>

<UserPlus size={17}/>

<span>
Get started
</span>

</Link>


</>

)

}


</div>



</div>


</header>

);

}