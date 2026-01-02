import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const ProfilePage = () => {
    const [profile, setProfile] = useState({
        full_name: '',
        role: '',
        experience: '',
        bio: '',
        skills: []
    });
    const [newSkill, setNewSkill] = useState('');
    const [loading, setLoading] = useState(true);
    const [certificates, setCertificates] = useState([]); // This would come from backend in a real app if we had an endpoint for it
    const [isEditing, setIsEditing] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

        try {
            // First get the user to see if we're authenticated and get user ID
            const userRes = await fetch('http://localhost:8000/api/me', {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (!userRes.ok) throw new Error('Failed to fetch user');
            const userData = await userRes.json();

            // If we had a specific endpoint to list all certificates, we'd call it here
            // For now we rely on what's in the profile or just show what's uploaded in this session for demo if not persisted in profile relation perfectly yet
            if (userData.profile) {
                setProfile(userData.profile);
            }
            setLoading(false);

        } catch (error) {
            console.error(error);
            // navigate('/login');
            setLoading(false);
        }
    };

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        try {
            const res = await fetch('http://localhost:8000/api/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(profile)
            });
            const data = await res.json();
            setProfile(data);
            setIsEditing(false);
        } catch (error) {
            console.log('Error updating profile:', error);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('description', 'User Certificate');

        const token = localStorage.getItem('token');
        try {
            const res = await fetch('http://localhost:8000/api/upload', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`
                },
                body: formData
            });
            const data = await res.json();
            if (res.ok) {
                alert("Certificate uploaded successfully!");
                // Ideally refresh certificates list here
            }
        } catch (error) {
            console.error('Upload failed:', error);
        }
    };

    const addSkill = () => {
        if (newSkill && !profile.skills.includes(newSkill)) {
            setProfile({ ...profile, skills: [...profile.skills, newSkill] });
            setNewSkill('');
        }
    };

    const removeSkill = (skillToRemove) => {
        setProfile({ ...profile, skills: profile.skills.filter(s => s !== skillToRemove) });
    };

    if (loading) return <div className="text-white text-center mt-20">Loading...</div>;

    return (
        <div className="min-h-screen bg-dark text-white p-8 pt-24">
            <div className="max-w-4xl mx-auto rounded-2xl glass-panel p-8 border border-white/10">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-secondary">
                        User Profile
                    </h1>
                    <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="bg-white/10 hover:bg-white/20 px-4 py-2 rounded-lg transition-colors"
                    >
                        {isEditing ? 'Cancel' : 'Edit Profile'}
                    </button>
                </div>

                {isEditing ? (
                    <form onSubmit={handleUpdateProfile} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-gray-400 mb-2">Full Name</label>
                                <input
                                    type="text"
                                    value={profile.full_name || ''}
                                    onChange={e => setProfile({ ...profile, full_name: e.target.value })}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2"
                                />
                            </div>
                            <div>
                                <label className="block text-gray-400 mb-2">Current Role</label>
                                <input
                                    type="text"
                                    value={profile.role || ''}
                                    onChange={e => setProfile({ ...profile, role: e.target.value })}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2"
                                />
                            </div>
                            <div>
                                <label className="block text-gray-400 mb-2">Experience</label>
                                <input
                                    type="text"
                                    value={profile.experience || ''}
                                    onChange={e => setProfile({ ...profile, experience: e.target.value })}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2"
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-gray-400 mb-2">Bio</label>
                            <textarea
                                value={profile.bio || ''}
                                onChange={e => setProfile({ ...profile, bio: e.target.value })}
                                className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 h-32"
                            />
                        </div>

                        <div>
                            <label className="block text-gray-400 mb-2">Skills</label>
                            <div className="flex gap-2 mb-2">
                                <input
                                    type="text"
                                    value={newSkill}
                                    onChange={e => setNewSkill(e.target.value)}
                                    className="flex-1 bg-black/40 border border-white/10 rounded-lg px-4 py-2"
                                    placeholder="Add a skill..."
                                />
                                <button type="button" onClick={addSkill} className="bg-primary px-4 rounded-lg">Add</button>
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {profile.skills.map((skill, idx) => (
                                    <span key={idx} className="bg-white/10 px-3 py-1 rounded-full text-sm flex items-center gap-2">
                                        {skill}
                                        <button type="button" onClick={() => removeSkill(skill)} className="text-red-400 hover:text-red-300">×</button>
                                    </span>
                                ))}
                            </div>
                        </div>

                        <button type="submit" className="bg-primary hover:bg-primary-dark px-6 py-2 rounded-lg font-bold">
                            Save Changes
                        </button>
                    </form>
                ) : (
                    <div className="space-y-6">
                        <div className="flex items-start gap-6">
                            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center text-3xl font-bold">
                                {profile.full_name ? profile.full_name[0] : 'U'}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">{profile.full_name || 'Anonymous User'}</h2>
                                <p className="text-primary text-lg">{profile.role || 'No role set'}</p>
                                <p className="text-gray-400 text-sm mt-1">{profile.experience || 'No experience info'}</p>
                            </div>
                        </div>

                        <div className="bg-white/5 rounded-xl p-6">
                            <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-3">About</h3>
                            <p className="text-gray-300 leading-relaxed">{profile.bio || 'No bio available.'}</p>
                        </div>

                        <div className="bg-white/5 rounded-xl p-6">
                            <h3 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-3">Skills</h3>
                            <div className="flex flex-wrap gap-2">
                                {profile.skills.length > 0 ? profile.skills.map((skill, idx) => (
                                    <span key={idx} className="bg-primary/20 text-primary border border-primary/30 px-3 py-1 rounded-full text-sm">
                                        {skill}
                                    </span>
                                )) : <p className="text-gray-500 italic">No skills added yet.</p>}
                            </div>
                        </div>
                    </div>
                )}

                <div className="mt-8 pt-8 border-t border-white/10">
                    <h3 className="text-xl font-bold mb-4">Certificates & Verification</h3>
                    <div className="bg-white/5 rounded-xl p-6 border-dashed border-2 border-white/20 hover:border-primary/50 transition-colors">
                        <label className="flex flex-col items-center justify-center cursor-pointer py-8">
                            <span className="text-gray-400 mb-2">Click to upload certificates (PDF, JPG, PNG)</span>
                            <input type="file" onChange={handleFileUpload} className="hidden" />
                            <div className="bg-white/10 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-white/20 transition-colors">
                                Select File
                            </div>
                        </label>
                    </div>
                    {/* List uploaded certificates link here if we fetched them */}
                </div>
            </div>
        </div>
    );
};

export default ProfilePage;
