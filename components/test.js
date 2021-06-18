let points = [];
let test1 = [0.1,0.9,20,0.5];
let test2 = [0.2,0.8,20,0.5];
let test3 = [0.3,0.7,20,0.5];
let test4 = [0.05,0.95,20,0.5];

points.push(test1)
points.push(test2)
points.push(test3)
points.push(test4)
console.log(points);

points = points.sort((a,b)=> ((a[0]>b[0])?1:a[0]==b[0]?0:-1));

console.log(points);