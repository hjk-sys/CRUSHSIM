<<<<<<< HEAD
# SeaSim
=======
# CRUSHSIM

<h1>Problem and Inspiration</h1>
<p>An estimated 20% of the ocean has been explored, meaning 80% of the ocean is unknown to science. The most problematic issues regarding exploration is depth, bringing freezing temperatures, no visibility, and insurmountable amounts of pressure[1]. In fact, with every 10 meters dived, pressure is increased by around 1 atmosphere, meaning, if you went to the bottom of the Mariana Trench, nearly 7 miles (11265.4 meters) deep, you feel the weight of around 30000 NVIDIA Shields on you! There is only 1 active manned submersible, Deepsea Challenger, that can reach a depth of 11000m, with the second best, Jiao Long, reaching 7000m[2]. To unlock the scientific unkowns of the ocean, we must master the force of pressure deep under the sea.</p>

<h1>What is CRUSHSIM?</h1>
<p>CRUSHSIM is an interactive simulation of the force of pressure underwater of given materials, objects, and even organisms. We can first select the shape, object, or organism, then the material, if not an organism. The program then calculates or simmulates the depth at which it will crack under deep underwater pressure. With CRUSHSIM, we can test different materials and change our understanding of how effective different materials and shapes will be given harsh depths. With this simmulation, we can actively study the effects of different depths on different materials in order to find a cheaper, more efficient, or a better submersible overall.</p>

<h1>How did we build it?</h1>
<p>Using python and an additional installation, pygame, we coded a simulation for yield strength of certain objects. Using a several different formulas for different object types, we use a material's compressive strength, the size of the object, the internal pressure of the object, the depth as it travels, and a constant variable that provides a yield strength of a given object's shape to calculate and simulate the depth at which the object will be crushed under the immense pressures of water. We also took advantage of much research that has already been conducted in order to find these constants and corroborate our program to be at the highest accuracy we can achieve.</p>

<h1>Challenges</h1>
<p> We both had similar challenges, being waking up early while going to bed late and lots of bugs and issues in our code. However we were able to push through these issues with the great mentors and valuable lessons and skills we had access to during the 36 hours. During our creation we were stuck at screen selection and organization of our dictionaries. Our code quickly began to get clunky and difficult to organize, this made our 5 different screen selections to make the code nearly indecipherable. We needed to and continue to require better ways at organizing, simply meaning we needed to use less variables and just make the million different functions simpler and more task-oriented. Originally, we wanted to prompt the user for any different kind of object and return the crushing depth at which it would crush, unfortunately it was quite complicated and we didn't like the results we got since it wasn't as visual as we had intended. Eventually though, we were able to organize and surface better solutions to our problems, such as working on screen selection and changing the physics so that the code is less clunky.</p>

<h1>Accomplishments</h1>
<p>We are proud of the final product we have produced. We've created a fun and interactive simulation of the undeniable strength of the pressures of the depths. Throughout our 36 hours, we were able to augment AI into our research and organization, perservering through frusterating bugs, and trying to compete with others. We believe our product of the simmulation is not quite finished but is a fun framework of what it could be if we continued to work on it.</p>

<h1>What we've learned</h1>
<p>During our research and project production we learned valuable life skills and information regarding oceanic issues. Communication, leadership, teamwork, coding, and technical skills are all required in the process of this 32 hour hackathon. After a while, Hamish finally figured out how to work pygame and install it, learning it while we went. Hunter gained valuable leadership skills as he facilitated group interaction and objectives. Overall, this experience has taught us both valuable lessons that we might not have learned elsewhere.</p>

<h1>Future of CRUSHSIM</h1>
<p>In the future, we hope to add more varaibles to account for different types of objects. We wish to improve the accuracy of our simmulation with real world experiments, learning physics, and having a better understanding of how different materials withstand compression. We could use the help of skilled professionals in coding and physics to create a better simmulation that's more accurate and provides helpful results so that we can explore the wildly unkown sea containing multitudes of undiscovered organisms. </p>

<h1>Acknoledgements</h1>
<P>Special thanks to all the staff, mentors, sponsors, and leadership that helped us brainstorm and eliminate issues during our work and allow this experience to happen.</P>

<h1>Resources</h1>
[1]https://oceana.org/blog/why-does-so-much-ocean-remain-unexplored-and-unprotected/<br>
[2]https://www.mtsmuv.org/active-manned-submersibles-by-depth
>>>>>>> e2a4b8d6cee6827ccfd73d02ac2be053760660d6
